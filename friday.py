import time
import pyttsx3
import speech_recognition as sr
from langchain_ollama import ChatOllama
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import Tool
# --- NEW LANGCHAIN 1.0 IMPORTS ---
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# --- 1. INITIALIZE VOICE ENGINE (TTS) ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')

voice_found = False
for voice in voices:
    if "Hazel" in voice.name or "Susan" in voice.name or "Great Britain" in voice.name:
        engine.setProperty('voice', voice.id)
        voice_found = True
        break

if not voice_found and len(voices) > 1:
    engine.setProperty('voice', voices[1].id) 

engine.setProperty('rate', 175)

def speak(text):
    print(f"\nFRIDAY: {text}")
    engine.say(text)
    engine.runAndWait()

# --- 2. INITIALIZE LISTEN ENGINE (STT) ---
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    with mic as source:
        print("\n[Listening...]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        print("[Processing speech...]")
        query = recognizer.recognize_google(audio)
        print(f"You said: {query}")
        return query
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        print("Network error with speech recognition.")
        return None

# --- 3. CONFIGURE FRIDAY'S BRAIN & TOOLS ---
speak("Initializing systems. Connecting to local core.")

llm = ChatOllama(model="qwen2.5:7b", temperature=0.2)

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
python_repl = PythonREPL()
python_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands to do accurate math, physics equations, or logic.",
    func=python_repl.run,
)
tools = [wikipedia, python_tool]

# --- 4. THE NEW LANGCHAIN 1.0 AGENT ---
# We no longer need long ReAct prompts! We just set a system prompt and a checkpointer for memory.
memory = InMemorySaver()
system_prompt = "You are FRIDAY, a superhuman scientist assistant. You are analytical, brilliant, and concise. You MUST use your tools to accurately answer questions or execute calculations."

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory
)

# Create a session ID so she remembers the conversation history across interactions
config = {"configurable": {"thread_id": "friday_session_1"}}

speak("FRIDAY is fully online. Systems operational.")

# --- 5. THE MAIN VOICE LOOP ---
while True:
    user_input = listen()
    
    if not user_input:
        continue
        
    if "exit" in user_input.lower() or "quit" in user_input.lower():
        speak("Shutting down systems. Goodbye.")
        break
        
    print("\nFRIDAY is calculating...")
    try:
        # The new invoke syntax automatically manages memory via the config thread!
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
        )
        
        # The agent returns a dictionary of messages. The last one is FRIDAY's answer.
        final_answer = response["messages"][-1].content
        
        speak(final_answer)
        
    except Exception as e:
        print(f"Error executing command: {e}")
        speak("I encountered an error processing that request.")