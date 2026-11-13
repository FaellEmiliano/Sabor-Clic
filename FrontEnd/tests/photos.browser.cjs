// Start backend/tests/serve_fixture.py first; requires Playwright and Chromium.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const {chromium}=require('playwright');

test('photos: library, upload, reuse, edit, remove and customer menu',async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
  try {
    const page=await browser.newPage({viewport:{width:1100,height:850}});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    const base=process.env.SABOR_QA_URL||'http://127.0.0.1:5051';
    const suffix=Date.now();
    const product='Produto foto '+suffix, ingredient='Ingrediente foto '+suffix;
    await page.goto(base);
    await page.locator('#loginEmail').fill('admin@teste.com');
    await page.locator('#loginPassword').fill('Teste1234');
    await page.locator('button[type=submit]').click();
    await page.waitForURL('**/admin_dashboard.html');
    await page.goto(base+'/admin_produtos.html');
    await page.getByRole('button',{name:'Adicionar',exact:true}).first().click();
    const dialog=page.locator('dialog');
    await dialog.locator('[name=nome]').fill(product);
    await dialog.locator('[name=preco]').fill('25.50');
    const stock=dialog.locator('[data-photo-path]').first();
    const stockPath=await stock.getAttribute('data-photo-path');
    await stock.click();
    assert.equal(await stock.getAttribute('aria-pressed'),'true');
    await dialog.getByRole('button',{name:'Salvar',exact:true}).click();
    await dialog.waitFor({state:'detached'});
    let row=page.getByRole('row').filter({hasText:product});
    await row.waitFor();
    assert.equal(await row.locator('img').getAttribute('src'),stockPath);

    await page.goto(base+'/admin_ingredientes.html');
    await page.getByRole('button',{name:'Adicionar',exact:true}).click();
    await dialog.locator('[name=nome]').fill(ingredient);
    await dialog.locator('[name=unidade_medida]').fill('kg');
    // Client validation leaves the dialog open and lets the administrator recover.
    await dialog.locator('[data-photo-file]').setInputFiles({name:'invalid.svg',mimeType:'image/svg+xml',buffer:Buffer.from('<svg/>')});
    assert.match(await dialog.locator('[role=alert]').textContent(),/JPEG/);
    await dialog.locator('[data-photo-file]').setInputFiles(path.join(__dirname,'../assets/img/products/nhoque.jpg'));
    await page.waitForFunction(()=>document.querySelector('[data-photo-preview]').src.startsWith('data:'));
    const uploaded=page.waitForResponse(r=>r.url().endsWith('/api/imagens')&&r.request().method()==='POST');
    await dialog.getByRole('button',{name:'Salvar',exact:true}).click();
    const uploadResponse=await uploaded;
    assert.equal(uploadResponse.status(),201);
    const uploadPath=(await uploadResponse.json()).imagem.caminho;
    await dialog.waitFor({state:'detached'});
    row=page.getByRole('row').filter({hasText:ingredient});
    await row.waitFor();
    assert.equal(await row.locator('img').getAttribute('src'),uploadPath);
    await page.reload();
    row=page.getByRole('row').filter({hasText:ingredient});
    await row.getByRole('button',{name:'Editar',exact:true}).click();
    assert.equal(await dialog.locator('[name=imagem]').inputValue(),uploadPath);
    await dialog.getByRole('button',{name:'Deixar sem foto',exact:true}).click();
    await dialog.getByRole('button',{name:'Salvar',exact:true}).click();
    await dialog.waitFor({state:'detached'});
    await page.waitForFunction(name=>[...document.querySelectorAll('tr')].some(r=>r.textContent.includes(name)&&r.querySelector('img')?.getAttribute('src')==='/assets/img/sem-foto.svg'),ingredient);

    await page.goto(base+'/admin_produtos.html');
    row=page.getByRole('row').filter({hasText:product});
    await row.getByRole('button',{name:'Editar',exact:true}).click();
    await dialog.locator(`[data-photo-path="${uploadPath}"]`).click();
    await dialog.getByRole('button',{name:'Salvar',exact:true}).click();
    await dialog.waitFor({state:'detached'});
    await page.reload();
    row=page.getByRole('row').filter({hasText:product});
    await row.waitFor();
    assert.equal(await row.locator('img').getAttribute('src'),uploadPath);
    await row.getByRole('button',{name:'Editar',exact:true}).click();
    fs.mkdirSync(path.join(__dirname,'../../output'),{recursive:true});
    await page.screenshot({path:path.join(__dirname,'../../output/fotos-cadastro.png'),fullPage:true});
    await dialog.getByRole('button',{name:'Cancelar',exact:true}).click();
    await page.evaluate(async()=>{
      await api('/logout',{method:'POST',body:{}});
      await api('/login',{method:'POST',body:{email:'cliente@teste.com',senha:'Teste1234'}});
    });
    await page.goto(base+'/cliente_cardapio.html');
    const card=page.locator('.card').filter({has:page.getByRole('heading',{name:product,exact:true})});
    await card.waitFor();
    const img=card.locator('img');
    assert.equal(await img.getAttribute('src'),uploadPath);
    assert.equal(await img.evaluate(image=>image.complete&&image.naturalWidth>0),true);
    assert.deepEqual(errors,[]);
  } finally {await browser.close();}
});
