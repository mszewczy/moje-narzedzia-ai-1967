First, tell about:

1. What type of app or website do you have in mind?

Ad. 2 Answer to the first question above: This is a tool for testing the Modern Google Docs Add-on framework in Google Cloud.
a. It also requires the Google Apps Script Editor syntax, current as of August 20, 2025, as described in https://developers.google.com/apps-script/release-notes, https://developers.google.com/apps-script/terms, https://developers.google.com/apps-script/samples, https://developers.google.com/apps-script/, and includes additional commands and their syntaxes for the following Google services:
https://www.googleapis.com/auth/script.container.ui, https://www.googleapis.com/auth/documents.currentonly, https://www.googleapis.com/auth/script.external_request

2. What is the main goal or purpose? (What is it supposed to do and who is it intended for?)
2.1 Are there any specific features or functionalities you'd like to include?

Announcement: 2 Answer to the two question: Despite the change in the programming procedure, I still have a problem with the Google Apps Script Editor syntax, which is currently being deprecated by Google as of August 20, 2025, because the "appsscript.json" manifest file returns the following error when trying to save the programming code: The "appsscript.json" file contains errors: Invalid manifest file - unknown fields: [addOns.common.menuItems]. 

Announcement: 2.1 Answer to the third clarifying question: The purpose of the Modern Google Docs Add-on framework in Google Cloud is to verify that, after opening any document, an additional option titled "My AI Tools (Cloud)" appears in Google Docs at https://docs.google.com/document in the top and right side menus, along with two test functions titled Function 1 and Function 2, which will execute when selected.
The application is designed for the Google Docs Add-on, specifically @gmail.com. Despite the change in programming procedures, I still have a problem with the Google Apps Script Editor syntax, which is currently deprecated by Google as of August 20, 2025. When attempting to save programming code, the "appsscript.json" manifest file returns the following error: "The file "appsscript.json" contains errors: Invalid manifest file – unknown fields: [addOns.common.menuItems].

PROMPT: I'm taking full advantage of Claude Opus 4.1, including the research and web search features, as well as the ability to verify code via MCP server Sentry.
Despite the change in the programming procedure, I still have a problem with the section titled Step 5: Create a Remote (New Apps Script Project),
specifically the subsection titled 4. Paste the Pilot Build Plan (appsscript.json): because the inserted code returns the following error: "The file "appsscript.json" contains errors: Invalid manifest file – unknown fields: [addOns.common.menuItems].

Taking full advantage of Claude Opus 4.1 with the Research (Extend thinking) features, including the Web search option, as well as the Sentry option,
i.e., the ability to verify code by the MCP Sentry server with the Seer Automation option enabled, which has access to this project published on GitHub
at https://github.com/mszewczy/moje-narzedzia-ai-1967.git, verify the code published on GitHub at https://github.com/mszewczy/moje-narzedzia-ai-1967.git
against the current syntax as of August 20, 2025. https://github.com/mszewczy/moje-narzedzia-ai-1967.git and automatically correct it to be 100% compatible
with the code syntax as of August 20, 2025, focusing on the manifest file called appsscript.json.

SETUP:

Step 1: Launch Google Cloud Shell Terminal
a. Open the Google Cloud Console:Click on this link:https://console.cloud.google.com/. Log in to the Google account you use for Google Docs.
b. Activate Cloud Shell:In the upper right corner of the screen, find and click the icon that looks like a small rectangle with a >_ symbol. This is the button"Activate Cloud Shell".
Step 2: Create a Project and Enable Tools (Commands)
a. Create a unique name for the project:Copy the command below, paste it into the terminal and press Enter.
export PROJECT_ID="my-ai-tools-1234"
b. Create a project:This command will create a new project with the name we just set.
gcloud projects create $PROJECT_ID --name="My Tools AI for Docs"
c. Set active project:We tell the terminal that from now on all commands should apply to this new project.
gcloud config set project $PROJECT_ID
d. Enable the necessary tools (API):This command will enable all the "safeties" needed for our add-on to function. It may ask for authorization – if so, click "AUTHORIZE."
gcloud services enable cloudfunctions.googleapis.com cloudbuild.googleapis.com run.googleapis.com docs.googleapis.com
Step 3: Preparing the "Engine" Code (Commands)
a. Create a package.json file:This file is a list of parts needed to build the "engine".
cat <<EOF > package.json
{
  "dependencies": {
    "@google-cloud/functions-framework": "^3.0.0",
    "googleapis": "^105.0.0"
  }
}
EOF


Create an index.js file:This is the complete code for our "engine".
cat <<EOF > index.js
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
console.log(\`Action received: \${action}\`);

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
EOF

All plans and parts are already in place.

Step 4: Implementing the "Engine" and Copying the Address (Command)
This is the final command in the terminal. It will trigger the construction and deployment of our "engine" in the cloud. We'll use the latest, second-generation Cloud Functions, which is faster and more modern.

a. Implement the function: Copy and paste the command below. This process will take a few minutes. Wait patiently until the terminal finishes and displays the green "OK" message.
gcloud functions deploy funkcje-dodatku-docs --gen2 --runtime=nodejs20 --region=europe-central2 --source=. --entry-point=handleRequest --trigger-http --allow-unauthenticated

b. Copy Engine Address:Once the deployment is complete, in the last lines of text in the terminal, find the line starting with URI:. 
The address on this line is the address of your "engine". Select it, copy it and save it in Notepad – we will need it in the next step!

Step 5: Create a Remote (New Apps Script Project)
Now we will create a "pilot" – an interface in Google Docs (menu and side panel) that will send commands to our new "engine" in the cloud.

a. Open the Apps Script Editor: Click on this link:https://script.google.com/home/my.
b. Create a New Project: In the upper left corner, click"+ New project".
c. Prepare Files:
  c'. Click on the icon Project Settings(sprocket) on the left side.
  c". Check the box"Show 'appsscript.json' manifest file in editor".
  Return toEditor (icon <>).
d. Paste the Pilot Build Plan (appsscript.json):
Click on the appsscript.json file.
Delete all its contents and paste the code below.
{
  "timeZone": "Europe/Warsaw",
  "dependencies": {},
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8",
  "oauthScopes": [
    "https://www.googleapis.com/auth/script.container.ui",
    "https://www.googleapis.com/auth/documents.currentonly",
    "https://www.googleapis.com/auth/script.external_request"
  ],
  "addOns": {
    "common": {
"name": "My AI Tools (Cloud)",
      "logoUrl": "http://idz.do/mszewczy32",
      "menuItems": [
        {
"text": "Show information (Function 1)",
          "functionName": "runShowAlert"
        },
        {
"text": "Insert text (Function 2)",
          "functionName": "runInsertText"
        }
      ]
    },
    "docs": {
      "homepageTrigger": {
        "runFunction": "onDocsHomepage"
      }
    }
  }
}

e. Paste the Pilot Code (Code.gs):
   Click on the Code.gs file.
   Delete all its contents and paste the code below.
  VERY IMPORTANT:In the first line of code, in the place of HERE_PASTE_YOUR_FUNCTION_URL, paste the URL you copied in the previous step.
  const CLOUD_FUNCTION_URL = 'PASTE_YOUR_FUNCTION_URL_HERE';
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

f. Save Project: Click the floppy disk icon (Save Project).

Step 6: Launch and Test
We are on the home stretch!
a. Deploy Pilot:
  In the Apps Script editor, in the upper right corner, click Deploy > New Deployment.
  Next to "Select type" click the gear icon and select "Google Workspace Add-on".
  Enter a description, e.g. Version 1.0 - Cloud.
  Click"Implement".
  You will need to grant permissions. Click "Authorize access", select your account, and on the "Google hasn't verified this app" screen,
  click"Advanced" and then"Go to ... (unsafe)" and at the end "Allow"This is standard procedure for custom add-ons.
  
b. Testing:
OpennewGoogle Doc or refresh an existing one.
Wait a moment. A new menu should appear at the top:"My AI Tools (Cloud)".
An icon with your photo should appear on the right.
Test all four options (two in the top menu and two in the side panel after clicking the icon).

Congratulations!Your add-on now runs on the modern, stable and scalable Google Cloud infrastructure. 



All plans and parts are already in place.
