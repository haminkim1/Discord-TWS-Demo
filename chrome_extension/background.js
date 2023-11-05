  // this listener executes contentScript.js where message.action === 'manualTest' and if the user manually enter into the Discord tab on Chrome
  // The URL is a test channel used to test functionality of the extension.
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('https://discord.com/')) {
      chrome.tabs.sendMessage(tabId, { action: 'manualTest' });
    }
  });

  // If multiple messages are sent at once, the listener fails to listen for every single message and may miss the latest messages. 
  // However, this happens if the messages are sent within seconds. 
  // Having a timer set to 5s may help retrieve messages sent at once altogether.   
  setInterval(() => sendNotificationToOpenChannels(5000), 5000);
  setInterval(() => sendNotificationToOpenChannels(8080), 5000);

function sendNotificationToOpenChannels(portNo) {
  // Check if the local Flask server is active
  console.log(portNo)
  fetch(`http://127.0.0.1:${portNo}`)
    .then(response => {
      if (response.ok) {
        // Fetch successful, now query for open Discord channel tabs
        chrome.tabs.query({ url: 'https://discord.com/channels/*' }, tabs => {
          tabs.forEach(tab => {
            chrome.tabs.sendMessage(tab.id, { action: 'triggerNotificationToAllRegisteredAndOpenTabs', portNo: portNo });
          });
        });
      }
    })
    .catch(error => {
      // Fetch failed, local Flask server is not active
    });
}
