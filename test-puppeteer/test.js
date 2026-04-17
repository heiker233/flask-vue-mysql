const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  page.on('requestfailed', request => console.log('REQUEST FAILED:', request.url(), request.failure().errorText));

  // Navigate to login
  await page.goto('http://localhost:5173/');

  // Wait for login form
  await page.waitForSelector('input[placeholder="请输入用户名"]');
  await page.type('input[placeholder="请输入用户名"]', 'admin');
  await page.type('input[placeholder="请输入密码"]', '123456');
  await page.click('.submit-btn');

  // Wait for login success and home page
  await new Promise(r => setTimeout(r, 2000));
  console.log('Logged in. Now clicking customers menu...');

  // Find customers menu item
  await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('.el-menu-item'));
    const customerItem = items.find(item => item.textContent.includes('客户管理'));
    if (customerItem) customerItem.click();
  });

  await new Promise(r => setTimeout(r, 2000));
  
  await browser.close();
})();
