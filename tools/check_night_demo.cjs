// Optional UI verification. Uses a supplied Playwright install; not a bot dependency.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 const out=path.resolve(__dirname,'../night-demo/verification');fs.mkdirSync(out,{recursive:true});
 const context=await browser.newContext({viewport:{width:1440,height:1100},colorScheme:'light'});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 try{
 await page.goto(process.env.DEMO_URL || 'http://127.0.0.1:8765/night-demo/index.html');
 await page.getByRole('heading',{name:'同一波机器人，两种决策'}).waitFor();
 assert.equal(await page.locator('#episodes').textContent(),'72');
 await page.getByRole('button',{name:'下一回合'}).click();
 assert.equal(await page.locator('#roundLabel').textContent(),'1 / 60');
 await page.getByRole('button',{name:'播放',exact:true}).click();
 await page.waitForFunction(()=>Number(document.querySelector('#turn').value)>=3);
 await page.getByRole('button',{name:'暂停',exact:true}).click();
 await page.locator('#turn').evaluate(e=>{e.value='30';e.dispatchEvent(new Event('input',{bubbles:true}))});
 const geometry=await page.locator('.arenas').boundingBox();
 await page.getByLabel('显示主题').selectOption('light');
 await page.screenshot({path:path.join(out,'light.png'),fullPage:true});
 await page.getByLabel('显示主题').selectOption('dark');
 assert.deepEqual(await page.locator('.arenas').boundingBox(),geometry);
 await page.screenshot({path:path.join(out,'dark.png'),fullPage:true});
 await page.getByLabel('显示主题').selectOption('system');
 await page.emulateMedia({colorScheme:'dark'});
 await page.waitForFunction(()=>document.documentElement.dataset.theme==='dark');
 await page.emulateMedia({colorScheme:'light'});
 await page.waitForFunction(()=>document.documentElement.dataset.theme==='light');
 await page.getByLabel('选择回放局面').selectOption('1');
 assert.equal(await page.locator('#roundLabel').textContent(),'0 / 60');
 await page.locator('#turn').evaluate(e=>{e.value='60';e.dispatchEvent(new Event('input',{bubbles:true}))});
 assert.equal(await page.getByRole('button',{name:'下一回合'}).isDisabled(),true);
 await page.getByRole('button',{name:'重置'}).click();
 assert.equal(await page.locator('#roundLabel').textContent(),'0 / 60');
 await page.setViewportSize({width:390,height:844});
 await page.locator('#turn').evaluate(e=>{e.value='30';e.dispatchEvent(new Event('input',{bubbles:true}))});
 for(const theme of ['light','dark']){
  await page.getByLabel('显示主题').selectOption(theme);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.screenshot({path:path.join(out,`mobile-${theme}.png`),fullPage:true});
 }
 assert.deepEqual(errors,[]);
 const report={browser:await browser.version(),desktop:[1440,1100],mobile:[390,844],
 themes:['light','dark','system'],checks:['play-pause','step','seek','reset','scenario-change','end-disabled','theme-layout-stability','no-horizontal-overflow','no-page-errors'],screenshots:4};
 fs.writeFileSync(path.join(out,'ui-checks.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
