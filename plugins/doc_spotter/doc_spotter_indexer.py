# plugins/doc_spotter/doc_spotter_indexer.py
import os
import logging
from pymongo import MongoClient
from modules.token_system import TokenSystem
from modules.allowed_chats import allowed_chats_only
from modules.configurator import get_env_var_from_db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
from plugins.doc_spotter.doc_spotter_file_manager import delete_indexed_files_callback, process_file_deletion, done_forwarding_files, start_file_deletion

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

token_system = TokenSystem(os.getenv("MONGODB_URI"), "Echo", "user_tokens")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["Echo_Doc_Spotter"]

def docspotter_command(update: Update, context: CallbackContext) -> None:
    doc_spotter_plugin_enabled_str = get_env_var_from_db('DOC_SPOTTER_PLUGIN')
    doc_spotter_plugin_enabled = doc_spotter_plugin_enabled_str.lower() == 'true' if doc_spotter_plugin_enabled_str else False

    if doc_spotter_plugin_enabled:
        keyboard = [
            [InlineKeyboardButton("Index Files", callback_data='index_files')],
            [InlineKeyboardButton("Set Up Listening Groups", callback_data='setup_group')],
            [InlineKeyboardButton("Setup F-Sub for Listening Group(s)", callback_data='setup_fsub')],
            [InlineKeyboardButton("Manage Index/Listen/F-Sub Chats", callback_data='manage_indexers')],
            [InlineKeyboardButton("Delete Indexed Files", callback_data='delete_indexed_files')],
            [InlineKeyboardButton("Add/Edit Buttons for Files", callback_data='dc_setup_buttons_f_files')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Doc Spotter Main Menu: 🔎', reply_markup=reply_markup)
    else:
        update.message.reply_text("Doc Spotter Plugin Disabled by the Person who deployed this Echo variant 💔")

def manage_indexers_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Manage Index Channel(s)", callback_data='dsi_manage_index_channels')],
        [InlineKeyboardButton("Manage Listening Group(s)", callback_data='dsi_manage_listening_groups')],
        [InlineKeyboardButton("Manage F-Sub Chat(s)", callback_data='dsi_manage_fsub_chats')],
        [InlineKeyboardButton("Back", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Now Choose an option to proceed", reply_markup=reply_markup)

def manage_index_channels_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    indexed_channels = list(client["Echo_Doc_Spotter"]["Indexed_Channels"].find({"user_id": user_id}))
    keyboard = []

    if not indexed_channels:
        keyboard.append([InlineKeyboardButton("No Indexed Channels Found", callback_data='no_action')])
    else:
        for channel in indexed_channels:
            channel_id = channel["channel_id"]
            try:
                chat_info = context.bot.get_chat(channel_id)
                chat_name = chat_info.title
            except Exception as e:
                logging.error(f"Error fetching chat {channel_id}: {e}")
                chat_name = "Channel"
            button_label = f"{chat_name} [{channel_id}]"
            keyboard.append([InlineKeyboardButton(button_label, callback_data=f'dsi_channel_{channel_id}')])

    keyboard.append([InlineKeyboardButton("Back", callback_data='dsi_back_to_indexers')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Here are your Indexed Channels:", reply_markup=reply_markup)

def manage_listening_groups_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    listening_groups = list(client["Echo_Doc_Spotter"]["Listening_Groups"].find({"user_id": user_id}))
    keyboard = []

    if not listening_groups:
        keyboard.append([InlineKeyboardButton("No Listening Groups Found", callback_data='no_action')])
    else:
        for group in listening_groups:
            group_id = group["group_id"]
            try:
                chat_info = context.bot.get_chat(group_id)
                chat_name = chat_info.title
            except Exception as e:
                logging.error(f"Error fetching chat {group_id}: {e}")
                chat_name = "Group"
            button_label = f"{chat_name} [{group_id}]"
            keyboard.append([InlineKeyboardButton(button_label, callback_data=f'dsi_group_{group_id}')])

    keyboard.append([InlineKeyboardButton("Back", callback_data='dsi_back_to_indexers')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Here are your Listening Groups:", reply_markup=reply_markup)

def manage_fsub_chats_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    fsub_chats = list(client["Echo_Doc_Spotter"]["Fsub_Chats"].find({"user_id": user_id}))
    keyboard = []

    if not fsub_chats:
        keyboard.append([InlineKeyboardButton("No F-Sub Chats Found", callback_data='no_action')])
    else:
        for fsub_chat in fsub_chats:
            fsub_chat_id = fsub_chat["chat_id"]
            try:
                chat_info = context.bot.get_chat(fsub_chat_id)
                chat_name = chat_info.title
            except Exception as e:
                logging.error(f"Error fetching chat {fsub_chat_id}: {e}")
                chat_name = "Chat"
            button_label = f"{chat_name} [{fsub_chat_id}]"
            keyboard.append([InlineKeyboardButton(button_label, callback_data=f'dsi_fsub_{fsub_chat_id}')])

    keyboard.append([InlineKeyboardButton("Back", callback_data='dsi_back_to_indexers')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Here are your F-Sub chats:", reply_markup=reply_markup)

def back_to_main_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    # Prepare the original keyboard layout
    keyboard = [
        [InlineKeyboardButton("Index Files", callback_data='index_files')],
        [InlineKeyboardButton("Set Up Group(s) to Begin Spotting", callback_data='setup_group')],
        [InlineKeyboardButton("Setup F-Sub for Listening Group(s)", callback_data='setup_fsub')],
        [InlineKeyboardButton("Manage Index/Listen/F-Sub Chats", callback_data='manage_indexers')],
        [InlineKeyboardButton("Delete Indexed Files", callback_data='delete_indexed_files')],
        [InlineKeyboardButton("Add/Edit Buttons for Files", callback_data='dc_setup_buttons_f_files')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message:
        query.edit_message_text(text='Select Process Mode for Doc Spotter Module:', reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Select Process Mode for Doc Spotter Module:', reply_markup=reply_markup)

def setup_fsub_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    text = """<b>🎧 Let's Set Up F-Sub for Your Listening Group(s)!</b>

1️⃣ <b>Add me to your F-Sub chat</b> [channel/group] as an admin. 👤
2️⃣ <b>Send the Telegram ID of your F-Sub chat.</b> 🔢"""
    keyboard = [[InlineKeyboardButton("Back", callback_data='back_to_main')]]  
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    context.user_data['awaiting_fsub_chat_id'] = True 

def channel_selected_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    channel_id = query.data.split('_')[2]  
    query.answer()

    confirmation_message = f"Are you want to stop indexing and delete the selected channel from my database?"
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=f'dsi_delete_channel_{channel_id}')],  
        [InlineKeyboardButton("No", callback_data='dsi_manage_index_channels')]  
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=confirmation_message, reply_markup=reply_markup)

def group_selected_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    group_id = query.data.split('_')[2]  
    query.answer()

    confirmation_message = f"Do you want me to stop listening and delete the selected group from my database?"
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=f'dsi_delete_group_{group_id}')],
        [InlineKeyboardButton("No", callback_data='dsi_manage_listening_groups')]  
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=confirmation_message, reply_markup=reply_markup)

def fsub_selected_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.data.split('_')[2]
    query.answer()

    confirmation_message = "Do you want to stop using and delete the selected F-Sub chat from my database?"
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=f'dsi_delete_fsub_{chat_id}')],
        [InlineKeyboardButton("No", callback_data='dsi_manage_fsub_chats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=confirmation_message, reply_markup=reply_markup)

def delete_channel_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    channel_id = query.data.split('_')[3]  
    result = db["Indexed_Channels"].delete_one({"channel_id": channel_id})
    if result.deleted_count > 0:
        query.answer("Channel removed.")
        logger.info(f"🗑️ Indexed channel deleted: {channel_id} by user {update.effective_user.id}")
    else:
        query.answer("Failed to remove channel or channel not found.")
    manage_index_channels_callback(update, context)

def delete_group_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    group_id = query.data.split('_')[3]  
    result = db["Listening_Groups"].delete_one({"group_id": group_id})
    if result.deleted_count > 0:
        query.answer("Group removed.")
        logger.info(f"🗑️ Listening group deleted: {group_id} by user {update.effective_user.id}")
    else:
        query.answer("Failed to remove group or group not found.")
    manage_listening_groups_callback(update, context)

def delete_fsub_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.data.split('_')[3]
    result = db["Fsub_Chats"].delete_one({"chat_id": chat_id})
    if result.deleted_count > 0:
        query.answer("F-Sub chat removed.")
        logger.info(f"🗑️ F-Sub chat deleted: {chat_id} by user {update.effective_user.id}")
    else:
        query.answer("Failed to remove F-Sub chat or chat not found.")
    manage_fsub_chats_callback(update, context)

def setup_group_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    text = """<b>🔧 Setup Instructions</b>

📌Topics are also supported. Send your topic ID along with your chat ID. Do not forget to put a space between chat id and topic id. Example: <code>-100123456789 123</code>

1️⃣ <b>Add me to your listening group as an admin.</b> 🛠️
2️⃣ <b>Then, send me your group's ID.</b> 🆔 (It should start with -100, e.g., -1001654958246)"""
    keyboard = [[InlineKeyboardButton("Back", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    context.user_data['awaiting_group_id'] = True  

def index_files_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("File ID - Method 1 (Quick)", callback_data='setup_channel')],
        [InlineKeyboardButton("MSG ID - Method 2 (Recommended)", callback_data='index_channel_method_2')],
        [InlineKeyboardButton("Back", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="""<b><i>Choose a method from below to index your channel,</i></b>
    
⚡ Method 1 - <i>Utilize File ID to process the user requests.</i> It will work even if the bot is not in the source chat after the index. However, indexed files may become unusable or unable to be sent to the user after some time. <code>May not work across the bots. if you change the bot-indexed file may not work for that bot</code> (there are downsides of using File ID)

💎 Method 2 - <i>Utilize Message ID and Chat ID to process requests.</i> This method does not expire over time like Method 1, but if you delete the file from the source chat, the bot will be unable to send the file to the requested user. As long as you keep your files safe in the source chat, this method works fine. <code>Working across the bots. You can safely change the bots and the indexed files work perfectly for that bot too</code>

For long-term use, the recommended method is <code>Method 2</code>.""", reply_markup=reply_markup,  parse_mode=ParseMode.HTML)

def setup_channel_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer("This method is quice and has less respond time, but indexed files may not work after sometime.", show_alert=True)
    text = """<b>🔧 Setup Instructions</b>

1️⃣ <b>Add me to your source channel as an admin.</b> 🛠️
2️⃣ <b>Then, send me your channel's ID.</b> 🆔 (It should start with -100, e.g., -1001654958246)

⚠️ <u>Important Notes:</u>
♦️<i>If the chat is a group and you want to clone messages from bots,</i> <b>this won't work</b>. <i>Telegram does not allow capturing messages sent by bots.</i>
♦️<i>Solution: If you want to clone messages sent by bots, use channels. Echo can catch the bot's message sent in channels</i>"""
    keyboard = [[InlineKeyboardButton("Back", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    context.user_data['awaiting_channel_id'] = True  

def setup_buttons_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    buttons_config_str = get_buttons_configuration(user_id)
    btn_cfg_text = f"""<u>🔗 URL Buttons for Files (DS Sub Plugin)</u>

<i>Now, send the buttons for your file(s). Use the ' - ' to separate button text from the URL, and ' | ' to place buttons side by side. To start a new line of buttons, Type in a new line.</i>

For example:
<code>Website - https://example.com | Help - https://example.com/help</code>
<code>Contact - https://example.com/contact</code>

<b>This will provide a 3 Buttons format. (Website & Help in 1st line, Contact in 2nd line)</b>

♦️ <i>Current Button(s) list</i>;
<code>{buttons_config_str}</code>"""
    btn_cfg_edited_text = query.edit_message_text(text=btn_cfg_text, parse_mode=ParseMode.HTML)
    context.user_data['btn_cfg_need_to_edit_msg_id'] = btn_cfg_edited_text.message_id
    context.user_data['awaiting_button_config'] = True

def is_bot_admin_in_channel(bot, chat_id) -> bool:
    try:
        chat = bot.get_chat(chat_id)
        if chat.type != 'channel':
            return False  
        
        member = bot.get_chat_member(chat_id, bot.id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logging.error(f"Failed to get bot's status or chat type for {chat_id}: {e}")
        return False

def is_bot_admin_in_group(bot, chat_id) -> bool:
    try:
        chat = bot.get_chat(chat_id)
        if chat.type not in ['group', 'supergroup']:
            return False  
        
        member = bot.get_chat_member(chat_id, bot.id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logging.error(f"Failed to get bot's status or chat type for {chat_id}: {e}")
        return False

def is_bot_admin_in_chat(bot, chat_id) -> bool:
    try:
        member = bot.get_chat_member(chat_id, bot.id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logging.error(f"Failed to get bot's status in the chat {chat_id}: {e}")
        return False

def index_channel_method_2_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer("This method is great if your source chat files are not deleted. If the source chat file is deleted, this method cannot access it.", show_alert=True)
    keyboard = [[InlineKeyboardButton("Back", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = query.edit_message_text(text="Now send a Temp Chat ID starts with '-100' for act as In-between transfer platform.\n\nMake sure bot is an admin with delete files and post message\n\n<code>Can be a Group chat or a Channel, Both accepted.</code>", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    context.user_data['awaiting_temp_chat_id'] = True
    context.user_data['temp_chat_id_setup_msg_id'] = msg.message_id

def handle_text(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    text = update.message.text.strip()
    user_id = update.message.from_user.id

    if user_data.get('awaiting_channel_id'):
        if text.startswith('-100'):
            if is_bot_admin_in_channel(context.bot, text):
                success = store_channel_id(user_id, text)
                if success:
                    update.message.reply_text(f"🗂️Index Channel <code>{text}</code> saved successfully. From now I will index every file you send to this chat.", parse_mode=ParseMode.HTML)
                    user_data['awaiting_channel_id'] = False  
                else:
                    update.message.reply_text(f"⚠️The Channel ID <code>{text}</code> is already configured by another user. So you cannot add that. If you think this was a mistake please contact the bot owner.", parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text("❌ Please provide a valid channel ID where I am an admin.")
        else:
            update.message.reply_text("❌Please try again! Provide a valid chat ID starting with -100.")

    elif user_data.get('awaiting_group_id'):
        parts = text.split()
        if len(parts) == 1 and parts[0].startswith('-100'):
            chat_id = parts[0]
            topic_id = None
        elif len(parts) == 2 and parts[0].startswith('-100'):
            chat_id, topic_id = parts[0], parts[1]
        else:
            update.message.reply_text("❌ Please provide a valid chat ID (starting with -100) and an optional topic ID.")
            return

        if is_bot_admin_in_group(context.bot, chat_id):
            success = store_group_id(user_id, chat_id, topic_id)
            if success:
                reply_text = f"👂Listening Group <code>{chat_id}</code> saved successfully."
                if topic_id:
                    reply_text += f"\n\nTopic ID <code>{topic_id}</code> is also saved."
                update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)
                user_data['awaiting_group_id'] = False
            else:
                update.message.reply_text(f"⚠️The Group ID <code>{chat_id}</code> is already configured by another user. So you cannot add that. If you think this was a mistake, please contact the bot owner.", parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text("❌ The provided ID does not belong to a group where I'm an admin. Please provide a valid group ID where I am an admin.")

    elif user_data.get('awaiting_fsub_chat_id'):
        if text.startswith('-100'):
            if is_bot_admin_in_chat(context.bot, text):
                store_fsub_chat_id(user_id, text)
                update.message.reply_text(f"🔮 F-Sub chat setup completed. Now, every user who uses Doc Spotter in your listing groups must join the <code>{text}</code> chat in order to use Doc Spotter.", parse_mode=ParseMode.HTML)
                user_data['awaiting_fsub_chat_id'] = False  
            else:
                update.message.reply_text("❌ The provided ID does not belong to a chat where I'm an admin. Please provide a valid chat ID where I am an admin.")
        else:
            update.message.reply_text("❌ Please try again! Provide a valid chat ID starting with -100.") 

    elif user_data.get('awaiting_button_config'):
        try:
            try:
                update.message.delete()
            except Exception as e:
                logger.error(f"Failed to delete user message: {e}")
            button_lines = text.split('\n')
            for line in button_lines:
                buttons = line.split('|')
                for btn in buttons:
                    parts = btn.split('-')
                    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                        raise ValueError("Invalid button format detected")
                        
            save_buttons_configuration(update.effective_user.id, text)
            need_to_edit_msg_id = context.user_data['btn_cfg_need_to_edit_msg_id']
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=need_to_edit_msg_id, text="Your button(s) list saved successfully ✅", parse_mode=ParseMode.HTML)
            user_data['awaiting_button_config'] = False
            context.user_data.clear()
        except Exception as e:
            try:
                update.message.delete()
            except Exception as e:
                logger.error(f"Failed to delete user message: {e}")
            update.message.reply_text("Invalid format. Please send your URL buttons in the correct format and try again.", parse_mode=ParseMode.HTML)
            
    elif user_data.get('awaiting_temp_chat_id'):
        if text.startswith('-100'):
            if is_bot_admin_in_chat(context.bot, text):
                user_data['temp_chat_id_m2'] = text
                chat_id = update.message.chat_id
                message_id = context.user_data['temp_chat_id_setup_msg_id']
                try:
                    update.message.delete()
                except Exception as e:
                    logger.error(f"Failed to delete user message: {e}")
                msg = context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Now send the chat id of the need to index channel.")
                context.user_data['temp_chat_id_setup_msg_id'] = msg.message_id
                context.user_data.pop('awaiting_temp_chat_id', None)
                user_data['awaiting_m2_index_chat_id'] = True
            else:
                update.message.reply_text("❌ Please provide a valid chat ID where I am an admin.")
        else:
            update.message.reply_text("❌ Please try again! Provide a valid chat ID starting with -100.")

    elif user_data.get('awaiting_m2_index_chat_id'):
        if text.startswith('-100'):
            if is_bot_admin_in_channel(context.bot, text):
                chat_info = context.bot.get_chat(text)
                chat_name = chat_info.title
                success = store_index_channel_method_2(user_id, user_data['temp_chat_id_m2'], text)
                if success:
                    chat_id = update.message.chat_id
                    message_id = context.user_data['temp_chat_id_setup_msg_id']
                    try:
                        update.message.delete()
                    except Exception as e:
                        logger.error(f"Failed to delete user message: {e}")
                    msg = context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"New Channel {chat_name} saved for index using method 2 🧬")
                    context.user_data.pop('awaiting_index_chat_id', None)
                    context.user_data.pop('temp_chat_id_setup_msg_id', None)
                else:
                    update.message.reply_text("Hmm... Look like another user already configured the temp chat or source channel before you provided.\n\nIf you think this was a mistake contact Echo Owner")
                    context.user_data.clear()
            else:
                update.message.reply_text("❌ Please provide a valid CHANNEL ID where I am an admin.")
        else:
            update.message.reply_text("❌ Please try again! Provide a valid chat ID starting with -100.")
    
    else:
        pass  

def store_channel_id(user_id: int, channel_id: str):
    """Store each new channel ID in a separate document with safety check."""
    collection = db["Indexed_Channels"]
    exists = collection.find_one({"channel_id": channel_id})
    if exists and exists["user_id"] != user_id:
        logger.info(f"🔄 Channel ID {channel_id} is already configured by another user. Stopped duplicating")
        return False
    elif not exists:
        collection.insert_one({"user_id": user_id, "channel_id": channel_id})
        logger.info(f"📡 New indexed channel set: {channel_id} by user {user_id}")
        return True

def store_group_id(user_id: int, group_id: str, topic_id: str = None):
    collection = db["Listening_Groups"]
    exists = collection.find_one({"group_id": group_id})
    if exists and exists["user_id"] != user_id:
        logger.info(f"🔄 Group ID {group_id} is already configured by another user. Stopped duplicating")
        return False
    elif not exists:
        document = {"user_id": user_id, "group_id": group_id}
        if topic_id:
            document["topic_id"] = topic_id
        collection.insert_one(document)
        logger.info(f"👥 New listening group set: {group_id} by user {user_id}")
        return True
    return False

def store_fsub_chat_id(user_id: int, chat_id: str):
    collection = db["Fsub_Chats"]
    # Check for duplicates before insertion
    exists = collection.find_one({"user_id": user_id, "chat_id": chat_id})
    if not exists:
        collection.insert_one({"user_id": user_id, "chat_id": chat_id})
        logger.info(f"🔔 New Fsub chat set: {chat_id} by user {user_id}")

def save_buttons_configuration(user_id: int, button_config_str):
    collection = db["URL_Buttons_Sets"]
    # Store button sets with user ID
    collection.update_one({'user_id': user_id}, {'$set': {'buttons_raw': button_config_str}}, upsert=True)
    logger.info(f"Buttons set saved for user {user_id} 🔗")

def get_buttons_configuration(user_id):
    collection = db["URL_Buttons_Sets"]
    user_buttons_data = collection.find_one({'user_id': user_id})
    if user_buttons_data:
        return user_buttons_data['buttons_raw']
    else:
        return None  

def process_new_file(update: Update, context: CallbackContext) -> None:
    message = update.message if update.message is not None else update.channel_post
    if message is None or message.chat.type != 'channel':
        return

    chat_id = str(message.chat.id)

    indexed_channel = db["Indexed_Channels"].find_one({"channel_id": chat_id})
    if indexed_channel is None:
        return

    user_id = indexed_channel["user_id"]
    if "temp_chat_id" in indexed_channel:
        temp_chat_id = indexed_channel["temp_chat_id"]
    else:
        temp_chat_id = None

    if message.document or message.photo or message.video or message.audio or message.animation:
        proceed_using_method_2 = True if "temp_chat_id" in indexed_channel else False
        if proceed_using_method_2:
            use_method_2 = True
            file_info = extract_file_info(message, use_method_2)
            store_file_info_using_method_2(
                str(user_id), *file_info, proceed_using_method_2, temp_chat_id
            )
        else:
            use_method_2 = False
            file_info = extract_file_info(message, use_method_2)
            store_file_info(
                str(user_id), *file_info, proceed_using_method_2
            )

def extract_file_info(message, use_method_2):
    file, file_type = None, None
    if use_method_2:
        if message.document:
            file = message.document
        elif message.photo:
            file = message.photo[-1]
        elif message.video:
            file = message.video
        elif message.audio:
            file = message.audio
        elif message.animation:
            file = message.animation
        
        file_name = getattr(file, 'file_name', 'Unknown')
        msg_id = message.message_id
        chat_id = message.chat_id
        file_size = getattr(file, 'file_size', 0)
        mime_type = getattr(file, 'mime_type', 'Unknown')
        caption = message.caption if message.caption else ''

        return file_name, msg_id, chat_id, file_size, mime_type, caption
    else:
        if message.document:
            file = message.document
            file_type = 'document'
        elif message.photo:
            file = message.photo[-1]
            file_type = 'photo'
        elif message.video:
            file = message.video
            file_type = 'video'
        elif message.audio:
            file = message.audio
            file_type = 'audio'
        elif message.animation:  
            file = message.animation
            file_type = 'gif'
        else:
            return None
    
        file_id = file.file_id
        file_name = getattr(file, 'file_name', 'Unknown')
        file_size = getattr(file, 'file_size', 0)
        mime_type = getattr(file, 'mime_type', 'Unknown')
        caption = message.caption if message.caption else ''

        return file_id, file_name, file_size, file_type, mime_type, caption

def store_file_info(user_id, file_id, file_name, file_size, file_type, mime_type, caption, proceed_using_method_2):
    collection_name = f"DS_collection_{user_id}"
    collection = db[collection_name]
    collection.insert_one({
        "file_id": file_id,
        "file_name": file_name,
        "file_size": file_size,
        "file_type": file_type,
        "mime_type": mime_type,
        "caption": caption,
        "proceed_using_method_2": proceed_using_method_2
    })

def store_file_info_using_method_2(user_id, file_name, msg_id, chat_id, file_size, mime_type, caption, proceed_using_method_2, temp_chat_id):
    collection_name = f"DS_collection_{user_id}"
    collection = db[collection_name]
    collection.insert_one({
        "file_name": file_name,
        "msg_id": msg_id,
        "chat_id": chat_id,
        "file_size": file_size,
        "mime_type": mime_type,
        "caption": caption,
        "proceed_using_method_2": proceed_using_method_2,
        "transfer_temp_chat_id": temp_chat_id
    })

def store_index_channel_method_2(user_id: int, temp_chat_id: str, index_chat_id: str):
    collection = db["Indexed_Channels"]

    indexed_channel = collection.find_one({"channel_id": index_chat_id})
    if indexed_channel and indexed_channel["user_id"] != user_id:
        return False

    if indexed_channel and indexed_channel["user_id"] == user_id:
        return True
        
    collection.insert_one({
        "user_id": user_id,
        "temp_chat_id": temp_chat_id,
        "channel_id": index_chat_id
    })
    logger.info(f"📡 New indexed channel set with method 2: {index_chat_id} using temp chat {temp_chat_id} by user {user_id}")
    return True

def setup_ds_dispatcher(dispatcher):
    dispatcher.add_handler(token_system.token_filter(CommandHandler("docspotter", docspotter_command)))
    dispatcher.add_handler(token_system.token_filter(CommandHandler("erasefiles", start_file_deletion)))
    dispatcher.add_handler(CommandHandler("stop", allowed_chats_only(done_forwarding_files)))
    dispatcher.add_handler(CallbackQueryHandler(index_files_callback, pattern='^index_files$'))
    dispatcher.add_handler(CallbackQueryHandler(setup_channel_callback, pattern='^setup_channel$'))
    dispatcher.add_handler(CallbackQueryHandler(setup_group_callback, pattern='^setup_group$'))
    dispatcher.add_handler(CallbackQueryHandler(manage_indexers_callback, pattern='^manage_indexers$'))
    dispatcher.add_handler(CallbackQueryHandler(manage_index_channels_callback, pattern='^dsi_manage_index_channels$'))
    dispatcher.add_handler(CallbackQueryHandler(channel_selected_callback, pattern='^dsi_channel_'))
    dispatcher.add_handler(CallbackQueryHandler(delete_channel_callback, pattern='^dsi_delete_channel_'))
    dispatcher.add_handler(CallbackQueryHandler(manage_listening_groups_callback, pattern='^dsi_manage_listening_groups$'))
    dispatcher.add_handler(CallbackQueryHandler(group_selected_callback, pattern='^dsi_group_'))
    dispatcher.add_handler(CallbackQueryHandler(delete_group_callback, pattern='^dsi_delete_group_'))
    dispatcher.add_handler(CallbackQueryHandler(manage_fsub_chats_callback, pattern='^dsi_manage_fsub_chats$'))
    dispatcher.add_handler(CallbackQueryHandler(fsub_selected_callback, pattern='^dsi_fsub_'))
    dispatcher.add_handler(CallbackQueryHandler(delete_fsub_callback, pattern='^dsi_delete_fsub_'))
    dispatcher.add_handler(CallbackQueryHandler(setup_fsub_callback, pattern='^setup_fsub$'))
    dispatcher.add_handler(CallbackQueryHandler(manage_indexers_callback, pattern='^dsi_back_to_indexers$'))
    dispatcher.add_handler(CallbackQueryHandler(back_to_main_callback, pattern='^back_to_main$'))
    dispatcher.add_handler(CallbackQueryHandler(setup_buttons_callback, pattern='^dc_setup_buttons_f_files$'))
    dispatcher.add_handler(CallbackQueryHandler(index_channel_method_2_callback, pattern='^index_channel_method_2$'))
    dispatcher.add_handler(CallbackQueryHandler(delete_indexed_files_callback, pattern='^delete_indexed_files$'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.chat_type.private, handle_text), group=2)
    dispatcher.add_handler(MessageHandler(Filters.document, process_new_file), group=2)
    dispatcher.add_handler(MessageHandler(Filters.photo, process_new_file), group=2)
    dispatcher.add_handler(MessageHandler(Filters.video, process_new_file), group=2)
    dispatcher.add_handler(MessageHandler(Filters.audio, process_new_file), group=2)
    dispatcher.add_handler(MessageHandler(Filters.animation, process_new_file), group=2)
    dispatcher.add_handler(MessageHandler(Filters.chat_type.private & Filters.audio, process_file_deletion), group=6)
    dispatcher.add_handler(MessageHandler(Filters.forwarded & Filters.chat_type.private | Filters.chat_type.groups & (Filters.document | Filters.photo | Filters.video | Filters.animation), process_file_deletion), group=6)
