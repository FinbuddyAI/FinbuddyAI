from profile_analyzer import ProfileAnalyzer
import json

def test_profile_analyzer():
    # Sample conversation history
    conversation_history = [
        {
            "speaker": "Advisor",
            "content": "Hello! I'm your personal financial advisor. I'd like to help you get started with managing your finances better. Could you tell me about your main financial goals and what you hope to achieve?"
        },
        {
            "speaker": "User",
            "content": "save money"
        },
        {
            "speaker": "Advisor",
            "content": "Great! Saving money is a solid goal. Can you tell me about any specific saving targets you have in mind, like a certain amount or for a particular purpose?"
        },
        {
            "speaker": "User",
            "content": "50000 usd for buying a car"
        },
        {
            "speaker": "Advisor",
            "content": "That's a clear goal! How about your monthly saving target? What amount are you aiming to save each month towards that car?"
        },
        {
            "speaker": "User",
            "content": "500 per month"
        },
        {
            "speaker": "Advisor",
            "content": "Thank you for sharing that. Now, could you tell me a bit about yourself, like your age and employment status?"
        },
        {
            "speaker": "User",
            "content": "22, phd student"
        },
        {
            "speaker": "Advisor",
            "content": "Thanks for that information! Just to summarize, your main financial goal is to save $50,000 for a car, and you're aiming to put aside $500 each month. You're currently 22 years old and a PhD student."
        }
    ]
    
    # Initialize the analyzer
    analyzer = ProfileAnalyzer()
    
    # Analyze the conversation
    user_profile = analyzer.analyze_conversation(conversation_history)
    
    # Print the results
    print("\nAnalyzed User Profile:")
    print(json.dumps(user_profile, indent=2))
    
    # Save the profile
    saved_path = analyzer.save_analysis(user_profile)
    print(f"\nProfile saved to: {saved_path}")

if __name__ == "__main__":
    test_profile_analyzer()
