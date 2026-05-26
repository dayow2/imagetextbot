import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('API_KEY')  # For image generation API

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /start is issued."""
    await update.message.reply_text(
        'Hello! I generate images from text. Send me a description, and I\'ll create an image for you!'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /help is issued."""
    await update.message.reply_text(
        'Usage: Send me any text description, and I will generate an image.\n\n'
        'Examples:\n'
        '- "A cat sitting on a chair"\n'
        '- "Sunset over mountains"\n'
        '- "Cyberpunk city at night"'
    )

async def generate_image(prompt: str):
    """Generate image using Replicate API or similar service."""
    # Option 1: Using Replicate (SDXL)
    import replicate
    output = replicate.run(
        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        input={"prompt": prompt}
    )
    return output[0] if output else None
    
    # Option 2: Using Hugging Face API
    # API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    # headers = {"Authorization": f"Bearer {API_KEY}"}
    # response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    # return response.content

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages and generate images."""
    prompt = update.message.text
    chat_id = update.effective_chat.id
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")
    
    # Send initial message
    processing_msg = await update.message.reply_text(f"🎨 Generating image for: '{prompt}'\nPlease wait...")
    
    try:
        # Generate image
        image_url = await generate_image(prompt)
        
        if image_url:
            # Send generated image
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=f"✅ Generated for: {prompt}"
            )
        else:
            await update.message.reply_text("❌ Failed to generate image. Please try again.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ An error occurred. Please try again later.")
    finally:
        await processing_msg.delete()

def main():
    """Start the bot."""
    # Create Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
