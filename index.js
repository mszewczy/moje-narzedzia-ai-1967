const { google } = require('googleapis');

/**
* The main function that handles requests from the Google Docs add-on.
* Works like a telephone switchboard - checks which function the add-on is requesting,
* and triggers the appropriate action.
 */
exports.handleRequest = async (req, res) => {
// We set headers to enable communication (important!)
  res.set('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') {
    res.set('Access-Control-Allow-Methods', 'POST');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    res.set('Access-Control-Max-Age', '3600');
    res.status(204).send('');
    return;
  }

  const action = req.body.action;
console.log(`Action received: ${action}`);

  let responseMessage = {};

  try {
    switch (action) {
      case 'showAlert':
        responseMessage = { success: true, message: 'Alert action received.' };
        break;
      case 'insertText':
        responseMessage = { success: true, message: 'Text insertion action received.' };
        break;
      default:
throw new Error('Unknown action.');
    }
    res.status(200).json(responseMessage);
  } catch (error) {
console.error('An error occurred:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};
