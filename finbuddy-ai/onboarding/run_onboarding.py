import os
import sys
from onboarding_agent import OnboardingAgent
from profile_analyzer import ProfileAnalyzer
import json

def main():
    print("\n=== FinBuddy Onboarding Process ===")
    print("Welcome to FinBuddy! Let's get to know you better to help you track your spending and achieve your saving goals.")
    print("I'll ask you some questions about your financial situation and goals.")
    print("You can type 'quit' at any time to end the session.\n")
    
    print("Starting the onboarding process...\n")
    
    try:
        # Get the root directory
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        config_path = os.path.join(root_dir, "config_list.json")
        
        # Initialize the onboarding agent with the config path
        agent = OnboardingAgent(config_path=config_path)
        
        # Create the necessary agents
        agent.create_agents()
        
        # Start the onboarding process
        user_profile, is_complete = agent.start_onboarding()
        
        if is_complete:
            # Initialize the profile analyzer
            analyzer = ProfileAnalyzer()
            
            # Analyze the conversation and save the profile
            analyzed_profile = analyzer.analyze_conversation(agent.conversation_history)
            saved_path = analyzer.save_analysis(analyzed_profile)
            
            print(f"\n✅ Onboarding complete! Your profile has been saved to: {saved_path}")
            print("\nThank you for completing the onboarding process. You can now use FinBuddy to track your expenses and work towards your financial goals!")
        else:
            print("\n⚠️ Onboarding was not completed. Your information was not saved.")
            print("You can start the onboarding process again when you're ready.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Onboarding process interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 