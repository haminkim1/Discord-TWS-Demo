chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.action === 'triggerNotificationToAllRegisteredAndOpenTabs') {
    const portNo = message.portNo
    const currentURL = window.location.href;
    let channelAndServerID = getChannelAndServerID(currentURL);
    let channelID = channelAndServerID[0];
    let serverID = channelAndServerID[1];

    try {
      // Call the function to retrieve the previous message data
      const discordMessages = getDiscordMessagesFromBrowser();
      const previousMessagesData = await getMessageData(portNo, serverID, channelID);
      let appHasSent = true;
      let newMessagesData;
      let lastMessageID;
      let difference;

      // Length will only be 0 when first running the app. 
      // The if statement will initialize the flask server.
      if (previousMessagesData.length == 0) {
        lastMessageID = discordMessages[discordMessages.length - 2].id
        difference = 1;
      }
      else {
        appHasSent = false;
        
        // If true, the app has already tried extracting message data into options contracts. 
        // Therefore, the number of messages ready to be extracted are the new messages
        if (previousMessagesData.appHasSentAPIRequestToDiscord) {
          lastMessageID = previousMessagesData.messages[previousMessagesData.messages.length - 1].messageID
        }
        // Else if false, the app still hasn't extracted the previous message data. 
        // Therefore, the number of messages ready to be extracted are the new messages and the previous messages.  
        else {   
          lastMessageID = previousMessagesData.lastMessageID      
        }
        difference = getNumOfNewMessages(lastMessageID, discordMessages)
      }
      newMessagesData = sliceNewMessages(difference, discordMessages);
      storeMessageDataToFlaskServer(portNo, serverID, channelID, newMessagesData, difference, lastMessageID, appHasSent);
    } catch (error) {
      console.error('Error:', error);
    } 
  }
});


/**
 * Extracts channel and server id from the Discord URL. 
 * @param link Discord link
 * @returns channel and server id within the Discord URL
 */
function getChannelAndServerID(link) {
  const pattern = /\/(\d+)\/?$/;
  
  const matches = link.match(pattern);
  let channelID = null;
  let serverID = null;
  
  if (matches) {
    channelID = matches[1];
    const linkWithoutLastSet = link.substring(0, matches.index);
    const secondMatches = linkWithoutLastSet.match(pattern);
    if (secondMatches) {
      serverID = secondMatches[1];
    }
  }
  return [channelID, serverID];
}


/**
 * 
 * @param serverID id of the Discord server number
 * @param channelID id of the Discord channel number
 * @returns JSON that was stored from the url after a Discord notification. 
 */
async function getMessageData(portNo, serverID, channelID) {
  const url = `http://127.0.0.1:${portNo}/${serverID}/${channelID}/latest-messages`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}


/**
 * 
 * @returns an array where each Discord message is the element. 
 * The array only includes Discord messages, and ignores replied text contents. 
 */
/**
 * IMPORTANT!!!!
 * Often Discord updates their class names of their HTML tags. 
 * On 01/11/2023, Chrome extension failed to get Discord messages from browser until the class names were updated
 * to the correct names. 
 * In the future if it happens again, scan through HTML tags of any message container in the Discord webapp. 
 * You may find a container with id="message-content-{id}". 
 * If the properties of that container have a value on id (should be the same as the container id number
 * and innerText matches with the message content, then get any of the available classnames that every
 * message container has, as well as the replied message containers and update the class names in the code below. 
 */
function getDiscordMessagesFromBrowser() {
      // markup_a7e664 messageContent__21e69 are the class id for message container on discord. 
      const messageContainers = document.querySelectorAll('.messageContent__21e69');

      // Filter out elements containing repliedTextContent-2hOYMB as one of their class names. 
      // Messages that was replied to are also within the notificationElements array. Those arrays contain
      // repliedTextContent__75526 as one of their class names. Removing will prevent the extension to think old replied messages are latest messages
      return Array.from(messageContainers).filter(element => !element.classList.contains('repliedTextContent__75526'));
}


/**
 * 
 * @param difference number of new messages that was sent after the previous message 
 * was posted to the Flask server.
 * @param discordMessages array of Discord messages that was received from the Discord site in the browser.
 * @returns slices the discordMessages array where the number of elements sliced is the difference. 
 */
function sliceNewMessages(difference, discordMessages) {
    if (difference <= 0) {
      return []
    }
    else {
      return discordMessages.slice(-difference);
    }
}

/**
 * 
 * @param messageID the message ID of the latest message posted in the Flask server.
 * @param discordMessages array of Discord messages that was received from the Discord site in the browser.
 * @returns @param difference where it is the number of new messages that was sent after the previous message 
 * was posted to the Flask server. 
 */
function getNumOfNewMessages(messageID, discordMessages) {
  let difference = 0;
  for (let i = 1; i < discordMessages.length; i++) {
    if (messageID == discordMessages[discordMessages.length - i].id) {
      return difference;
    }
    else {
      difference++;
    }
  }
  return difference;
}


/**
 * Creates an object containing message id, message content, server id, channel id 
 * and difference (number of new messages compared to previous 5 messages)
 */
function storeMessageDataToFlaskServer(portNo, serverID, channelID, newMessagesData, difference, lastMessageID, appHasSent) {
  // Generate CSRF token
  const csrfToken = Math.random().toString(36).substring(2);

  // Send the data to Flask backend
  const url = `http://127.0.0.1:${portNo}/${serverID}/${channelID}/latest-messages`;
  const data = {
    messages: newMessagesData.map(el => ({
      message: el.innerText,
      messageID: el.id
    })),
    appHasSentAPIRequestToDiscord: appHasSent,
    channelID: channelID,
    difference: difference,
    lastMessageID: lastMessageID,
    serverID: serverID
  };

  if (data.difference != 0) {
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken
      },
      body: JSON.stringify(data)
    })
      .then(response => {
        if (response.ok) {
          console.log('Data stored in Flask backend');
        } else {
          console.log('Failed to store data in Flask backend');
        }
      })
      .catch(error => {
        console.log('Error:', error);
      });
  }
}
