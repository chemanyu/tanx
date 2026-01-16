// 定时任务：每30分钟自动更新一次cookie
const UPDATE_INTERVAL = 30; // 分钟

// 监听定时器触发
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'updateCookie') {
    console.log('定时更新Cookie任务触发:', new Date().toLocaleString());
    updateCookieAutomatically();
  }
});

// 扩展安装或更新时，创建定时器并立即执行一次
chrome.runtime.onInstalled.addListener(() => {
  console.log('Chrome扩展已安装/更新');
  
  // 创建定时器（每30分钟执行一次）
  chrome.alarms.create('updateCookie', {
    periodInMinutes: UPDATE_INTERVAL
  });
  
  console.log('定时器已创建，立即执行一次Cookie更新');
  updateCookieAutomatically();
});

// 扩展启动时，确保定时器存在
chrome.runtime.onStartup.addListener(() => {
  console.log('Chrome扩展启动');
  
  // 确保定时器存在
  chrome.alarms.create('updateCookie', {
    periodInMinutes: UPDATE_INTERVAL
  });
});

// 自动更新Cookie的函数
function updateCookieAutomatically() {
  // 获取当前活动的标签页
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    if (tabs.length === 0) {
      console.error('未找到活动标签页');
      // 如果没有活动标签页，尝试获取所有标签页中符合条件的
      chrome.tabs.query({}, function(allTabs) {
        // 查找淘宝或天猫相关的标签页
        const relevantTab = allTabs.find(tab => 
          tab.url && (tab.url.includes('taobao.com') || 
                     tab.url.includes('tmall.com') || 
                     tab.url.includes('alimama.com'))
        );
        
        if (relevantTab) {
          fetchAndSendCookies(relevantTab.url);
        } else {
          console.log('未找到相关页面，跳过本次更新');
        }
      });
      return;
    }

    const currentUrl = tabs[0].url;
    if (!currentUrl) {
      console.error('无法获取当前标签页URL');
      return;
    }

    fetchAndSendCookies(currentUrl);
  });
}

// 提取并发送Cookie的核心逻辑
function fetchAndSendCookies(url) {
  try {
    const currentUrl = new URL(url);
    const domain = currentUrl.hostname;
    const topLevelDomain = domain.split('.').slice(-2).join('.');

    console.log('正在获取域名的Cookie:', topLevelDomain);

    // 获取指定域名的所有cookies
    chrome.cookies.getAll({ domain: topLevelDomain }, function(cookies) {
      if (chrome.runtime.lastError) {
        console.error('获取Cookie失败:', chrome.runtime.lastError.message);
        return;
      }

      if (cookies.length === 0) {
        console.log('当前域名未找到Cookie:', topLevelDomain);
        return;
      }

      // 格式化cookies为字符串
      const cookieString = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
      
      console.log('Cookie获取成功，准备发送到后端...');

      // 发送到后端API
      const formData = new FormData();
      formData.append('cookie', cookieString);

      fetch('http://127.0.0.1:5003/update_cookie', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
      })
      .then(body => {
        console.log('Cookie更新成功:', body);
        // 可以选择发送通知
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon48.png',
          title: 'Cookie更新成功',
          message: `更新时间: ${new Date().toLocaleString()}`,
          priority: 1
        });
      })
      .catch(error => {
        console.error('发送Cookie失败:', error.message);
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon48.png',
          title: 'Cookie更新失败',
          message: error.message,
          priority: 2
        });
      });
    });
  } catch (error) {
    console.error('处理URL时出错:', error.message);
  }
}

// 监听来自popup的消息（可选，用于手动触发）
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'updateCookieNow') {
    updateCookieAutomatically();
    sendResponse({ status: 'started' });
  }
  return true;
});
