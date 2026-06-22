import time
import pyttsx3
import speech_recognition as sr
from langchain_ollama import ChatOllama
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool

# --- 1. INITIALIZE VOICE ENGINE (TTS) ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Hunt for the Windows British female voice (Hazel or Susan)
voice_found = False
for voice in voices:
    if "Hazel" in voice.name or "Susan" in voice.name or "Great Britain" in voice.name:
        engine.setProperty('voice', voice.id)
        voice_found = True
        break

# Fallback just in case the British voice isn't installed
if not voice_found and len(voices) > 1:
    engine.setProperty('voice', voices[1].id) 

engine.setProperty('rate', 175)  # Speaking speed

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

# The prompt now includes {chat_history} to keep everything in memory
template = """You are FRIDAY, a superhuman scientist assistant. You are analytical, brilliant, and concise.
You must use your previous conversation history and tools to assist the user with everything they ask.

Conversation History:
{chat_history}

Tools available:
{tools}

To use a tool, you MUST use the exact following format:

Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

When you have the final answer, or if you do not need a tool, use this format:

Thought: I now know the final answer
Final Answer: [your response here]

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- 4. MEMORY STORAGE ---
history_log = ""

speak("FRIDAY is fully online. Systems operational.")

# --- 5. THE MAIN VOICE LOOP ---
while True:
    # Trigger listening mode
    user_input = listen()
    
    if not user_input:
        continue
        
    if "exit" in user_input.lower() or "quit" in user_input.lower():
        speak("Shutting down systems. Goodbye.")
        break
        
    print("\nFRIDAY is calculating...")
    try:
        # Run the agent with the user input and the ongoing history log
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": history_log
        })
        
        final_answer = response['output']
        
        # Append this exchange to the memory so she remembers it next time
        history_log += f"\nUser: {user_input}\nFRIDAY: {final_answer}\n"
        
        # Speak the final answer out loud
        speak(final_answer)
        
    except Exception as e:
        print(f"Error executing command: {e}")
        speak("I encountered an error processing that request.")