 if gui_active:
        # Check for Chat GPT command
        if 'chat gpt' in query.lower():
            # Extract the user query after "chat gpt"
            user_query = query.lower().replace("chat gpt", "").strip()
            if user_query:
                # Call the Gemini API
                response = query_gemini_api(user_query)
                if "error" not in response:
                    # Process and speak the response
                    answer = response.get("contents", [{}])[0].get("parts", [{}])[0].get("text", "I couldn't find an answer.")
                    speak(answer)
                    assistant_window.update_text(f"Chat GPT: {answer}")
                else:
                    speak("Sorry, there was an error with the Gemini API.")
                    assistant_window.update_text("Error with Gemini API.")
            else:
                speak("Please provide a query after 'Chat GPT'.")
                assistant_window.update_text("No query provided after 'Chat GPT'.")
