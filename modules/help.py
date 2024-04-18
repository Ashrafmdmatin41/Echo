from telegram.ext import CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode

def help_command(update, context: CallbackContext) -> None:
    # Send the photo with the inline keyboard
    photo_path = 'assets/help.jpg' 
    caption = """Ah! The help menu, my fav! Select Help Category to Proceed:
    
_Echo the Multifunctional User assistant has arrived to save your schedule and make your life easier! Let's unlock your full memory potential with these magical features_✨"""

    keyboard = [
        [
            InlineKeyboardButton("Basics", callback_data='basic'),
            InlineKeyboardButton("Reminders", callback_data='reminder'),
            InlineKeyboardButton("Gemini AI", callback_data='gemini'),
        ],
        [
            InlineKeyboardButton("(Broad/Schedu)cast", callback_data='brsc'),
            InlineKeyboardButton("ChatBot", callback_data='chatbot_help'),
            InlineKeyboardButton("Calculator(s)", callback_data='calculator_help'),
        ],
        [
            InlineKeyboardButton("Telegraph Up", callback_data='tgphup'),
            InlineKeyboardButton("Logo Gen", callback_data='logogen_help'),
            InlineKeyboardButton("DocSpotter", callback_data='doc_spotter_help'),
        ],
        [
            InlineKeyboardButton("ShiftX", callback_data='shiftx_help'),
            InlineKeyboardButton("RemoveBG", callback_data='removebg_help'),
            InlineKeyboardButton("Info Feature", callback_data='info_help'),
        ],
        [
            InlineKeyboardButton("Commit Detector", callback_data='commit_detector_help'),
            InlineKeyboardButton("IMDb", callback_data='imdb_help'),
            InlineKeyboardButton("Clonegram", callback_data='clonegram_help'),
        ],
        [
            InlineKeyboardButton("F-Sub", callback_data='f_sub_help'),
            InlineKeyboardButton("FileFlex", callback_data='file_flex_help'),
            InlineKeyboardButton("Misc", callback_data='misc'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the photo with caption and the inline keyboard
    message = update.message.reply_photo(
        photo=open(photo_path, 'rb'),
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )

    # Save the message ID and an empty stack in user data to edit it later
    context.user_data['help_message_id'] = message.message_id
    context.user_data['category_stack'] = []

def handle_help_button_click(update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    # Define the messages for each button
    messages = {
           'basic': "*Basic Commands to Start Echo and manege it⚙️*\n\n"
                 "/start - Press this button to get this party started and receive a warm welcome!💫\n"
                 "/help - Feeling a bit lost? I'm always here to lend a helping hand!  Just ask, and I'll guide you through my powers.💁\n"
                 "/bsettings - Config Echo!⚙️ (OWNER Only)\n"
                 "/restart - Start Fresh Again. Restart Echo and Get Latest Updates from [Official Repo](https://github.com/theseekerofficial/Echo) (OWNER Only)🔁\n\n[Echo-Verse♾️](https://t.me/Echo_AIO)",
        'reminder': "*Welcome to Echo's Reminder Function Related Commands for your reminder manage⚙️*\n\n"
                    "_⭐Reminder Tip: Ready to ditch the default dings and bongs? Turn your reminders into sonic experiences with Echo's custom ringtone magic! Type /ringtones for more info_\n\n"
                    "_Recurring Reminder Support available for various time periods in /setreminder command_\n\n"
                    "/setreminder - Set a reminder for yourself using the modern method.🧬\n"
                    "/sr - Set a reminder for yourself using the traditional method.⏰\n"
                    "/myreminders - Show your existing reminders.📃\n"
                    "/delreminder - Delete a specific reminder.🗑️\n"
                    "/settimezone - Set your time zone.🌎\n"
                    "/editreminders - Edit your existing reminders.✂️\n\n🌟Easily find your timezone using [this link](https://telegra.ph/Choose-your-timezone-02-16)\n\n[Echo-Verse♾️](https://t.me/Echo_AIO)",
            'misc': "*Welcome to Echo's other misc commands⚙️*\n\n"
                "/ringtones - Explore sample ringtones.🎵\n"
                "/info - Get Info about specific User,Bot or Chat 📜\n"
                "/users - See Echo using Users Chats list 📜\n"
                "/database - See my mongoDB database stats📊\n"
                "/moreinfo - Get more information about the bot.📚\n"
                "/addpaid - Add paid users\n/paid - See paid users\n\n[Echo-Verse♾️](https://t.me/Echo_AIO)"
                "/cancel - Stop all ongoing operation states and clear cache user data 🧹\n\n[Echo-Verse♾️](https://t.me/Echo_AIO)",
            'brsc': """*Welcome to Echo's Announcement modules⚙️*\n\n"""
                 "/broadcast - Initiate a instant broadcast📢\n"
                 "/scheducast - Scheduled a broadcast for the future!🔮\n"
                 "/scd - The cmd used for capture schducast date and time. Use /scheducast to get this step🪜\n"
                 "/scm - The cmd used for capture schducast message. Use /scheducast to get this step🪜\n\n[Echo-Verse♾️](https://t.me/Echo_AIO)",
          'gemini': """*Welcome to Echo's Gemini AI Plugin*\n\n"""
                 "/gemini - Start chat with gemini AI💬\n"
                 "/mygapi - Get your Google Gemini API from [this link](https://aistudio.google.com/app/apikey) and send it to bot using (/mygapi yourapikey) format✅\n"
                 "/analyze4to - Start analyze your image using Gemini-Pro-Vision📸\n"
                 "/showmygapi - To see you current API stored in database🔗\n"
                 "/delmygapi - Delete your Google API🚮\n\n"
                 "[Echo-Verse♾️](https://t.me/Echo_AIO)",
 'calculator_help': """*Welcome to Echo's Calculator Plugin🧩*\n\n"""
                 "/calculator - To get calculator menu 🧮\n"
                 "/cal - Short cmd for /calculator cmd🔮\n\n"
                 "Most of the calculators in Echo use Telegram Inline buttons for gathering inputs. However, there are only /calculator and /cal commands available for this plugin.✅\n"
                 "You can find more informative help note in each calculator.🚀\n\n"
                 "[Echo-Verse♾️](https://t.me/Echo_AIO)",
          'tgphup': """*Welcome to Echo's Telegraph Upload Plugin🧩*\n\n"""
                 "Here is the command list for this plugin\n"
                 "/uptotgph - Reply to any Image as /uptotgph to initiate upload process🔮\n\n"
                 "Telegraph Upload Plugin is a simple plugin in the Echo. So currently it's only available /uptotgph command only, For now!.🚀✅\n\n"
                 "[Echo-Verse♾️](https://t.me/Echo_AIO)",
    'logogen_help': """*Welcome to Echo's Logo Gen Plugin🧩*\n\n"""
                 "⚠️ This plugin is still under development, and more improvements are yet to come.\n\n"
                 "/logogen - Start Crafting Your Logo🎨🖌️\n\n"
                 """🔰Describe how you want to create your logo. For an example let's think you want to get a logo for Echo in Red font in Black Background. Then you need to send cmd as `/logogen Red Echo in Black Background`\n\n"""
                 """🔰After You send cmd, the bot will show the "Select a Font for logo Generate" menu with Font Buttons. Choose your desired font for your logo📝\n"""
                 """🔰After, the bot will ask you about the "Graphics category", "Graphics pattern", "Font Size" and "Frame Selection". Choose your favorite options for creating your logo.🪄\n\n"""
                 "⚜️Explore all fonts, Graphics, Patterns, Font Sizes, and Frames to uncover the perfect match that reflects your style and uniqueness.✨\n"
                 "⚜️Refer Echo's [Official Repo wiki](https://github.com/theseekerofficial/Echo/wiki) to learn how to add your own Fonts, Graphics and Frame Templates!✨\n\n"
                 "[Echo-Verse♾️](https://t.me/Echo_AIO)",
'doc_spotter_help': """🚀 *Echo's Doc Spotter Comprehensive Guide*

*Admins:*
1. *Setup*: Add Echo bot as admin in your channel/group.
2. *Activate*: Send the unique channel/group ID to Echo.
3. *Command*: /docspotter main cmd
            : /erasefiles for delete files
            : /stop for stop deletion

*Users:*
*Search*: Just type any document/media name or keywords in the configured group.
*Results*: Echo lists all matching files.
*Access*: Click on your desired document from Echo’s list to get it in PM.
*F-Sub Requirement?*: Follow Echo's prompt to join necessary chats.

*Features:*
🗂 *Robust Indexing*: Echo smartly indexes files for quick retrieval.
🔍 *Effortless Searching*: Find exactly what you need with simple keywords.
📥 *Instant Access*: Receive files directly in PM for privacy.
🎥 *IMDb Insights*: For movie and TV files, Echo fetches IMDb details.
⚙️ *Inline Management*: Admins can easily manage indexing settings via inline buttons.
🔄 *Pagination*: Navigate through search results with 'Prev' and 'Next'.

[Echo-Verse♾️](https://t.me/Echo_AIO)""",
       'info_help': """📘 *The `/info` command can be used in several ways to retrieve information about users,bots and chats within Telegram:*

1️⃣ *Get Your Info*
Simply send `/info` in a private chat with the bot, and it will return your Telegram information, including your user ID, username (if any), and other relevant details.

2️⃣ *Get Info of Another User, Bot or chat*
Forward a user,bot or chat message to Echo's PM. Reply to it with `/info`. The bot will provide information about the user, bot or chat you replied to, including their ID, username, and more.

3️⃣ *Fetch Information Using Username or User ID*
You can also use `/info` followed by a username (e.g., `/info @username`) or a Telegram user ID (e.g., `/info 123456789`) to get information about that particular user or chat.

🔍 *More*
Maybe some chat's info not available due to privacy settings.

🤖 *Echo and Privacy*
Remember, Echo respects user privacy and Telegram's API limitations. Some information might not be retrievable in certain contexts due to these restrictions.

[Echo-Verse♾️](https://t.me/Echo_AIO)
""",
   'chatbot_help' : """🤖 *Welcome to Echo Chatbot!* 🗨️

_How to Use:_🪄

1. *Activate Chatbot:*
   - Use `/chatbot` to enable or disable the chatbot feature. 💬

2. *Chatting with the Bot:*
   - Once the chatbot is activated, start sending messages like you would in any chat.
   - The bot will respond to your messages using AI-generated content. 🤖

3. *API Key Setup:*
   - If you didn't setup and API key, use `/mygapi` command to configure your API key. 🔑
   - To get one go to [this link](https://aistudio.google.com/app/apikey).
   - After that click "Create API Key" button and copy your api
   - Now Send it along with /mygapi cmd. (E.g. `/mygapi 094t3h8g43209nhgvf4098t3gnhv8598gbnhe`)

4. *Getting Help:*
   - If you encounter any issues or need assistance, type `/help` to get guidance. ℹ️

5. *Enjoy Conversations:*
   - Have fun chatting with Echo Chatbot! Engage in conversations and explore its capabilities. 🎉

You can always deactivate the chatbot feature when you want. Just use `/chatbot` command again.

*Remember, Echo's Chat bot can reply to anything you send. I mean ANYTHING!*😉

[Echo-Verse♾️](https://t.me/Echo_AIO)
""",
   'commit_detector_help' : """*Commit Detector Feature Overview* 🔄

The *Commit Detector* is an exclusive feature tailored for the Echo's deployment owners, offering real-time monitoring of GitHub repositories for new commits.

🛠️ *Setup & Configuration:*
- `GH_CD_URLS`: A comma-separated list of GitHub repository URLs. Format - `theseekerofficial/Echo`
- `GH_CD_CHANNEL_IDS`: Telegram Channel/Group ID(s) where updates are sent, also comma-separated.
- `GH_CD_PAT`: Optional Personal Access Token for GitHub to boost your API rate limit and use authenticated requests.

🔄 *Operational Workflow:*
1. *Fetching Commits*: The bot periodically checks for the latest commits in the specified repositories.
2. *Commit Detection*: It detects new commits by comparing SHAs with the stored ones in the MongoDB `GH_Commit_Detector` collection.
3. *Notification*: For any new commit found, it sends a detailed update to the specified Telegram channels/groups.

This feature is a powerful tool for staying updated with GitHub repository changes directly within Telegram

[Echo-Verse♾️](https://t.me/Echo_AIO)
""",
   'shiftx_help' : """*ShiftX is Echo's feature that allows users to perform various file conversions in no time!.🔄*
   
*🚀 Start the ShiftX Plugin:*
- Type `/shiftx` in any private chat with the bot to start the ShiftX plugin.
- This command will display a menu with categories for documents, images, and audio. After that selected the category you want.

*🔳 Choose Conversion Type:*
- Depending on the category you selected, you'll be presented with different conversion options.
- For example, if you choose "Documents," you might see options like "PDF to Word," "PDF to TXT," etc.
- Click on the desired conversion type.

*⬆️ Upload File:*
- After selecting the conversion type, you'll be prompted to upload the file you want to convert.
- Upload the file by sending it to the bot.

*⬇️ Receive Converted File:*
- After the conversion is complete, the bot will send you the converted file.

[Echo-Verse♾️](https://t.me/Echo_AIO)
""",
   'removebg_help' : """*RemoveBG allows you to remove background from basically any image within few seconds!.🪄*
   
*Setting up Remove.bg API Key ⚙️*
- To set up your Remove.bg API key, use the command `/setrbgapi <your_api_key>`.
- Example: `/setrbgapi your_api_key_here`

*Removing Backgrounds🎨🖌️*
- To remove the background from an image, reply to the image with the command `/removebg`.
- Example: Reply to an image with `/removebg`.

*Viewing Remove.bg API Key 🔍*
To view your current Remove.bg API key, use the command `/showrbgapi`.
Example: `/showrbgapi`

*Deleting Remove.bg API Key 🚮*
If you wish to delete your Remove.bg API key, use the command `/delrbgapi`.
Example: `/delrbgapi`

*Checking API Usage 📊*
To check your Remove.bg API usage, use the command `/rbgusage`.
Example: `/rbgusage`

[Echo-Verse♾️](https://t.me/Echo_AIO)
""",
   'imdb_help' : """🔶*Welcome to the IMDb Plugin! Here's how you can start using it:*

*Performing a Search* 🔎

1. *Initiate Search*: To search for a movie or TV series, use the `/imdb` command followed by the name of the movie or series. For example: `/imdb Inception`
2. *View Results*: After a short moment, the bot will display the top 10 matching results for your query.
3. *Select a Result*: Click on the inline button corresponding to the movie or series you're interested in. 

_Tips_ ✔️

- *Search Again*: You can perform another search at any time by using the `/imdb` command followed by your new query.
- *Help and Support*: If you encounter any issues or have questions, Visit @ECHO_Support_Unit

Enjoy the IMDb Plugin!

[Echo-Verse♾️](https://t.me/Echo_AIO)
""",
   'clonegram_help' : """🔷*Welcome to the Clonegram Plugin! Here's how you can start using it:*

*Setup a Task* ⚙️

🔶 *Initiate Set up*: Simply send /clonegram and follow the guide provided by the bot. 
🔶 In this step you need to provide the source chat id , destination chat id (Use /info command to find your chat ids), clone type, and media types
🔶 After successful setup bot will start to clone your source chat to the destination chat

_Tips_ ✔️

Admin Role is required for channels. But for groups, it's unnecessary if the bot's 'Group Privacy' is disabled in @BotFather. Contact the deployed person to know about that

Enjoy the Clonegram Plugin!

[Echo-Verse♾️](https://t.me/Echo_AIO)
""",
   'f_sub_help' : """💨 *Welcome to F-Sub Plugin help! Here's how you can start using it:*

*Setup a Task* ⚙️

♦️ *Initiate Set up*: Simply send /fsub and follow the guide provided by the bot. 
♦️ In this step, you need to provide the monitoring chat ID (It must be a group chat ID) and check chat IDs (Both groups and channels support)
♦️ After successful setup, Echo will monitor every message in the monitor chat ID and check whether is user sub to checking chat or not

_Tips_ ✔️

Admin Role is required for both monitoring chat and checking chats

Enjoy the Clonegram Plugin!

[Echo-Verse♾️](https://t.me/Echo_AIO)
""",
   'file_flex_help' : """*📂 Welcome to FileFlex Plugin Help! Here's how you can start using it:*

*Managing Your File Templates and Jobs ⚙️*

♦️ Initiate Set up: Simply send /fileflex and choose a mode from the menu.
♦️ Instant Flex for quick flex, Pre-Config Flex for flex using Global Template
♦️ Add/Edit Template: Use this option to create or edit G-Templates for your files.
♦️ FileFlex Chat Job: Set up a job to automatically apply your templates to files shared within specific Telegram chats.
♦️ Delete Chat Jobs: Manage or delete existing jobs.

*Setting Up a Job 🛠️*
❄️ Click 'FileFlex Chat' Job, Provide a valid Telegram chat ID. The bot must be an admin in this chat.

*Using Templates 🖼️*
❄️ Select 'Add/Edit Template', Utilize placeholders like `{file__name}`, `{file__size}`, ... to craft your captions dynamically. Define buttons using a format Text - URL. You can create multiple rows of buttons for different links.

_Tips_ ✔️

Ensure the bot is an admin in chats where you want to automate file handling.

[Echo-Verse♾️](https://t.me/Echo_AIO)
"""
        
    }

    message_text = messages.get(data, "Sorry, no information available for this category.")

    keyboard = [[InlineKeyboardButton("Back", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_caption(
        caption=message_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )

    context.user_data['category_stack'].append(data)

def handle_back_button_click(update, context: CallbackContext) -> None:
    category_stack = context.user_data.get('category_stack', [])

    if category_stack:
        previous_category = category_stack.pop()

        previous_keyboard = get_inline_keyboard_for_category(previous_category)

        update.callback_query.edit_message_caption(
            caption="""Ah! The help menu, my fav! Select Help Category to Proceed:
    
Echo the Multifunctional User assistant has arrived to save your schedule and make your life easier! Let's unlock your full memory potential with these magical commands✨""",
            reply_markup=previous_keyboard
        )
    else:
        update.callback_query.edit_message_caption(
            caption="""Ah! The help menu, my fav! Select Help Category to Proceed:
    
Echo the Multifunctional User assistant has arrived to save your schedule and make your life easier! Let's unlock your full memory potential with these magical commands✨""",
            reply_markup=get_inline_keyboard_for_category(None)
        )

    context.user_data['category_stack'] = category_stack

def get_inline_keyboard_for_category(category):
    keyboard = [
        [
            InlineKeyboardButton("Basics", callback_data='basic'),
            InlineKeyboardButton("Reminders", callback_data='reminder'),
            InlineKeyboardButton("Gemini AI", callback_data='gemini'),
        ],
        [
            InlineKeyboardButton("(Broad/Schedu)cast", callback_data='brsc'),
            InlineKeyboardButton("ChatBot", callback_data='chatbot_help'),
            InlineKeyboardButton("Calculator(s)", callback_data='calculator_help'),
        ],
        [
            InlineKeyboardButton("Telegraph Up", callback_data='tgphup'),
            InlineKeyboardButton("Logo Gen", callback_data='logogen_help'),
            InlineKeyboardButton("DocSpotter", callback_data='doc_spotter_help'),
        ],
        [
            InlineKeyboardButton("ShiftX", callback_data='shiftx_help'),
            InlineKeyboardButton("RemoveBG", callback_data='removebg_help'),
            InlineKeyboardButton("Info Feature", callback_data='info_help'),
        ],
        [
            InlineKeyboardButton("Commit Detector", callback_data='commit_detector_help'),
            InlineKeyboardButton("IMDb", callback_data='imdb_help'),
            InlineKeyboardButton("Clonegram", callback_data='clonegram_help'),
        ],
        [
            InlineKeyboardButton("F-Sub", callback_data='f_sub_help'),
            InlineKeyboardButton("FileFlex", callback_data='file_flex_help'),
            InlineKeyboardButton("Misc", callback_data='misc'),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
