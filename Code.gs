// HERE_PASTE_YOUR_FUNCTION_URL, paste the URL you copied in the previous step.
const CLOUD_FUNCTION_URL = 'https://europe-central2-moje-narzedzia-ai-1967.cloudfunctions.net/funkcje-dodatku-docs';

// Functions called from the menu at the top
function runShowAlert() {
  callCloudFunction('showAlert');
DocumentApp.getUi().alert('Hello!', 'Function 1 has been successfully executed.', DocumentApp.getUi().ButtonSet.OK);
}

function runInsertText() {
  callCloudFunction('insertText');
  const cursor = DocumentApp.getActiveDocument().getCursor();
  if (cursor) {
cursor.insertText('Text inserted by Function 2.');
  } else {
DocumentApp.getActiveDocument().getBody().appendParagraph('Text inserted by Function 2 at the end of the document.');
  }
}

// Function that builds the sidebar
function onDocsHomepage() {
  var builder = CardService.newCardBuilder();
builder.setHeader(CardService.newCardHeader().setTitle('Quick Actions (Cloud)'));
  var section = CardService.newCardSection();
section.addWidget(CardService.newTextParagraph().setText('Use the buttons below to run the functions.'));

  var button1 = CardService.newTextButton()
.setText('Show information (Function 1)')
    .setOnClickAction(CardService.newAction().setFunctionName('runShowAlert'));

  var button2 = CardService.newTextButton()
.setText('Insert text (Function 2)')
    .setOnClickAction(CardService.newAction().setFunctionName('runInsertText'));

  section.addWidget(button1);
  section.addWidget(button2);
  builder.addSection(section);
  return builder.build();
}

// Helper function for communicating with our cloud "engine"
function callCloudFunction(actionName) {
  const payload = {
    action: actionName
  };
  const options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };

  try {
    const response = UrlFetchApp.fetch(CLOUD_FUNCTION_URL, options);
console.log('Response from Cloud Function:', response.getContentText());
  } catch (e) {
console.error('Error calling Cloud Function:', e);
DocumentApp.getUi().alert('An error occurred communicating with the server.');
  }
}
