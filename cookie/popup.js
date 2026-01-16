document.addEventListener('DOMContentLoaded', function() {
  const sendButton = document.getElementById('sendButton');
  const statusDiv = document.getElementById('status');
  const resultDiv = document.getElementById('result');

  sendButton.addEventListener('click', function() {
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';
    statusDiv.textContent = 'Fetching current tab...';

    // Get the current active tab
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs.length === 0) {
        showError('No active tab found.');
        return;
      }

       const currentUrl = new URL(tabs[0].url);
      const domain = currentUrl.hostname;
      const topLevelDomain = domain.split('.').slice(-2).join('.');
      statusDiv.textContent = 'Fetching cookies...';

      // Get all cookies for the current URL
      chrome.cookies.getAll({ domain: topLevelDomain }, function(cookies) {
        if (chrome.runtime.lastError) {
          showError('获取Cookie异常: ' + chrome.runtime.lastError.message);
          return;
        }
        // showError('123123==' + cookies);
        if (cookies.length === 0) {
          showError('当前页面未找到Cookie.');
          return;
        }

        // Format cookies as a semicolon-separated string (standard cookie format)
        const cookieString = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');

        statusDiv.textContent = 'Sending cookies to API...';
        // Send POST request to the API
        const formData = new FormData();
        formData.append('cookie', cookieString);
        
        fetch('http://127.0.0.1:5000/update_cookie', {
          method: 'POST',
          body: formData
        })
        .then(response => {
          if (!response.ok) {
            showError('HTTP error! status.');
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.text();  // Get the body as text; use .json() if the response is JSON
        })
        .then(body => {
          statusDiv.textContent = 'Success!';
          resultDiv.textContent = body;  // Display the response body
          resultDiv.style.backgroundColor = '#d4edda';
          resultDiv.style.borderColor = '#c3e6cb';
        })
        .catch(error => {
          showError('Error sending request: ' + error.message);
        })
        .finally(() => {
          sendButton.disabled = false;
          sendButton.textContent = '更新Cookie';
        });
      });
    });
  });

  function showError(message) {
    statusDiv.textContent = 'Error:';
    resultDiv.textContent = message;
    resultDiv.style.backgroundColor = '#f8d7da';
    resultDiv.style.borderColor = '#f5c6cb';
    sendButton.disabled = false;
    sendButton.textContent = '更新Cookie';
  }
});