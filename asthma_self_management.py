# Import libraries
import telegram
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, Filters
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


# Replace 'your_excel_file.xlsx' with the actual path to your Excel file
csv_file_path = 'Asthma_Symptoms.csv'
    
# Read the Excel file into a pandas DataFrame
df = pd.read_csv(csv_file_path)



# Define NLP functions
def tokenize_and_stem(text):
    # Tokenize the input text
    tokens = word_tokenize(text)

    # Stem each token using Porter Stemmer
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]

    return stemmed_tokens



# Define chatbot functions
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello and welcome! I am Ruby, your personal assistant for managing asthma!')
    update.message.reply_text('Prompt /help for assistance.')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Feel free to choose from two available commands based on your preference:\
                              \n1. /symptom: Use this command to discover the probability of you having asthma.\
                              \n2. /trigger: Use this command to discover the cause or trigger to your asthma attack.\
                              \n3. /treatment: Use this command to discover the recommended treatment for your current asthma condition.')
 


# Start to process user input        
def process_input(update: Update, context: CallbackContext) -> None:  
    user_input = update.message.text.lower()
    
    # Symptoms
    # Implement logic based on user input
    if user_input.startswith('/symptom'):

        # Ask the user for their current symptom
        update.message.reply_text('Please tell me your current symptom.')

        # Listen for the user's response
        context.user_data['waiting_for_symptom'] = True


    # Trigger
    # Implement logic based on user input
    elif user_input.startswith('/trigger'):
        # Ask about triggers
        update.message.reply_text('Can you tell me about your surroundings. For example:\
                                  \nYou can let me know if there are any bugs, furry animals, mice, ants etc. You can also let me know if you are in hazy, smoky areas, or if there are any smokers around you.\
                                  \n\nThis information will be collected to identify your specific triggers that worsen your symptoms?')

        # Set a flag for waiting for triggers
        context.user_data['waiting_for_triggers'] = True


    # Treatment
    # Implement logic based on user input
    elif user_input.startswith('/treatment'):
        # Ask about triggers
        update.message.reply_text('May I know your age? (In numerical format)')

        # Set a flag for waiting for triggers
        context.user_data['waiting_for_age'] = True


    elif context.user_data.get('waiting_for_symptom', False):
        # User has provided their current symptom
        context.user_data['waiting_for_symptom'] = False

        # Pass the user's input to the tokenize_and_stem function
        processed_input = tokenize_and_stem(user_input)

        # Access the 'Symptom' column
        symptom_data = df[['Symptom', 'Advice']].values
        
        detected_symptom = None
        symptom_advice = None

        for symptom, advice in symptom_data:
            symptom_words = tokenize_and_stem(symptom)
            if any(keyword in processed_input for keyword in symptom_words):
                detected_symptom = symptom
                symptom_advice = advice
                break

        if detected_symptom:
            update.message.reply_text(f'The probability of you having asthma is high. \n\n{symptom_advice}')

            # Patient age
            # Ask about triggers
            update.message.reply_text('Now, tell me about your surroundings. For example:\
                                      \nYou can let me know if there are any bugs, furry animals, mice, ants etc. You can also let me know if you are in hazy, smoky areas, or if there are any smokers around you.\
                                      \n\nThis information will be collected to identify your specific triggers that worsen your symptoms?')

            # Set a flag for waiting for triggers
            context.user_data['waiting_for_triggers'] = True

        else:
            update.message.reply_text('No specific symptom identified.')

            # Prompt the user if they need any other help
            update.message.reply_text('Do you need any other help? Prompt /help for assistance.')

            # Set a flag for waiting for additional help
            context.user_data['waiting_for_additional_help'] = True
    
    # Triggers
    elif context.user_data.get('waiting_for_triggers', False):
        # User is providing information about triggers
        context.user_data['waiting_for_triggers'] = False
        
        # Process the user's input for triggers
        processed_triggers = tokenize_and_stem(user_input)

        # Access the 'Triggers' column
        trigger_data = df[['Surrounding', 'Trigger','TriggerManage']].values
        
        # Check if the processed input contains relevant keywords
        detected_trigger = None
        trigger_manage = None

        for surrounding, trigger, manage in trigger_data:
            trigger_words = tokenize_and_stem(surrounding)
            if any(keyword in processed_triggers for keyword in trigger_words):
                detected_trigger = trigger
                trigger_manage = manage
                break

        if detected_trigger:
            update.message.reply_text(f'Your trigger may be {detected_trigger}. \n\nYou are advised to {trigger_manage}.')

            # Patient age
            # Ask about triggers
            update.message.reply_text('May I know your age? (In numerical format)')

            # Set a flag for waiting for triggers
            context.user_data['waiting_for_age'] = True

        else:
            update.message.reply_text('No specific symptom identified.')

            # Prompt the user if they need any other help
            update.message.reply_text('Do you need any other help? Prompt /help for assistance.')

            # Set a flag for waiting for additional help
            context.user_data['waiting_for_additional_help'] = True
    
    # Age
    elif context.user_data.get('waiting_for_age', False):
        # User has provided their current symptom
        context.user_data['waiting_for_age'] = False

        # Check the provided age
        age_input = user_input.strip()

        if age_input.isdigit():
            age = int(age_input)

            if age < 12:
                # Set a flag for waiting for frequency choices
                context.user_data['waiting_for_frequency'] = True

                # Define an inline keyboard with two buttons
                keyboard = [
                    [InlineKeyboardButton("Symptoms less than twice a month", callback_data='cfrequency1')],
                    [InlineKeyboardButton("Symptoms twice a month, or more but less than 4 - 5 days a week", callback_data='cfrequency2')],
                    [InlineKeyboardButton("Symptoms most days, or waking up with asthma one a week or more", callback_data='cfrequency3')],
                    [InlineKeyboardButton("Daily symptoms, or waking up with asthma once a week or more, and low lung function", callback_data='cfrequency4')]
                ]

                # Send a text message to the user along with the inline keyboard
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('You belong to the age group below 12 years, categorizing you as a child.\n\nCan you decide how frequently you experience asthma symptoms? Choose your frequency:', reply_markup=reply_markup)

            elif age >= 12:
                # Set a flag for waiting for frequency choices
                context.user_data['waiting_for_frequency'] = True

                # Define an inline keyboard with two buttons
                keyboard = [
                    [InlineKeyboardButton("Symptoms less than twice a month", callback_data='afrequency1')],
                    [InlineKeyboardButton("Symptoms twice a month, but less than daily", callback_data='afrequency2')],
                    [InlineKeyboardButton("Symptoms most days, or waking up with asthma one a week or more", callback_data='afrequency3')],
                    [InlineKeyboardButton("Symptoms most days, or waking up with asthma once a week or more, and low lung function", callback_data='afrequency4')]
                ]

                # Send a text message to the user along with the inline keyboard
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('So you are 12 years old or above, falling into the category of either an adult or an adolescent.\n\nCan you decide how frequently you experience asthma symptoms? Choose your frequency:', reply_markup=reply_markup)

        else:
            update.message.reply_text('Invalid age format.')

            # Prompt the user if they need any other help
            update.message.reply_text('Do you need any other help? Prompt /help for assistance.')

            # Set a flag for waiting for additional help
            context.user_data['waiting_for_additional_help'] = True

    
    # Check for waiting_for_additional_help
    elif context.user_data.get('waiting_for_additional_help', False):
        context.user_data['waiting_for_additional_help'] = False

        if user_input.startswith('/help'):
            help_command(update, context)

        else:
            update.message.reply_text('Okay! If you have any other questions, feel free to ask.')





#----------------------------------------------------------------------------------------------------------------------------------------------------------------------





# Age button callback
def frequency_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    frequency_choice = query.data
    context.user_data['frequency'] = frequency_choice

    advice_message = '\n\nPlease note that this is a general recommendation, and it\'s important to consult with your healthcare provider for personalized advice.'


    if frequency_choice == 'cfrequency1':
        context.bot.send_message(chat_id=query.message.chat_id, text=f'To manage your asthma symptoms, it is recommended to take the following treatment: \
                                 \nLow dose ICS. Take this treatment whenever you use your SABA (Short-Acting Beta-Agonist). {advice_message}')

    elif frequency_choice == 'cfrequency2':
        context.bot.send_message(chat_id=query.message.chat_id, text=f'To manage your asthma symptoms effectively, it is recommended to take the following treatment: \
                                 \nLow dose maintenance ICS. {advice_message}')
    
    elif frequency_choice == 'cfrequency3':
        context.bot.send_message(chat_id=query.message.chat_id, text=f'To effectively manage your asthma symptoms, it is advised to take the following treatment: \
                                 \nLow dose maintenance ICS-LABA. {advice_message}')
    
    elif frequency_choice == 'cfrequency4':
        context.bot.send_message(chat_id=query.message.chat_id, text=f'To effectively manage your asthma symptoms, it is advised to follow this treatment plan: \
                                 \nTake a medium or high dose maintenance ICS-LABA. {advice_message}')
    
    elif frequency_choice == 'afrequency1':
        context.bot.send_message(chat_id=query.message.chat_id, text=f'To manage your asthma symptoms, it is recommended to take the following treatment: \
                                 \nLow dose ICS. Take this treatment whenever you use your SABA (Short-Acting Beta-Agonist). {advice_message}')
    
    elif frequency_choice == 'afrequency2':
        context.bot.send_message(chat_id=query.message.chat_id, text=f'To manage your asthma symptoms effectively, it is recommended to take the following treatment: \
                                 \nDaily low dose inhaled corticosteroid (ICS). {advice_message}')
    
    elif frequency_choice == 'afrequency3':
        context.bot.send_message(chat_id=query.message.chat_id, text=f'To manage your asthma symptoms effectively,  it is recommended to consider the following treatment: \
                                 \nLow dose ICS LABA, or medium dose ICS, or very low dose ICS-formoterol maintenance and reliever (MART). {advice_message}')

    elif frequency_choice == 'afrequency4':
        context.bot.send_message(chat_id=query.message.chat_id, text=f'It is recommended that you consider taking the prescribed treatment: \
                                 \nMedium dose ICS LABA, or low dose ICS-formoterol maintenance and reliever therapy (MART). {advice_message}')
        
    # Prompt the user if they need any other help
    context.bot.send_message(chat_id=query.message.chat_id, text='Do you need any other help? Prompt /help for assistance.')

    # Set a flag for waiting for additional help
    context.user_data['waiting_for_additional_help'] = True





#----------------------------------------------------------------------------------------------------------------------------------------------------------------------




# Integrate with Telegram
def main():
    # Insert your Telegram bot token here
    bot_token = '6349187938:AAGh3RxDSoiIq562K4_PS0khuFvrOLo-wY8'

    updater = Updater(token=bot_token)
    # updater = Updater(token=bot_token, use_context=True, webhook=False)
    dp = updater.dispatcher

    # Register handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(None, process_input)) 
    dp.add_handler(CallbackQueryHandler(frequency_callback))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

# Step 8: Execute the main function
if __name__ == '__main__':
    main()
