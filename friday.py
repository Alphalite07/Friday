import time
import random
import pyttsx3
import speech_recognition as sr
from langchain_ollama import ChatOllama
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import Tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# --- NEW: TERMINAL UI ENGINE ---
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

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
    # Visually render FRIDAY's response in a glowing panel
    console.print(Panel(text, title="[bold cyan]F.R.I.D.A.Y.[/bold cyan]", border_style="cyan", padding=(1, 2)))
    engine.say(text)
    engine.runAndWait()

# --- 2. INITIALIZE LISTEN ENGINE (STT) ---
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    with mic as source:
        console.print("[dim italic]Listening for audio signature...[/dim italic]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        console.print("[dim magenta]Processing audio frame...[/dim magenta]")
        query = recognizer.recognize_google(audio)
        # Visually render your input in a clean green format
        console.print(f"[bold green]User:[/bold green] {query}")
        return query
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        console.print("[bold red][ERROR] Network connection to audio server lost.[/bold red]")
        return None

# --- 3. CONFIGURE FRIDAY'S BRAIN & TOOLS ---
console.print(Panel("[bold yellow]INITIALIZING CORE SYSTEMS...[/bold yellow]", border_style="yellow"))

llm = ChatOllama(model="qwen2.5:7b", temperature=0.2)

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
python_repl = PythonREPL()
python_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands to do accurate math, physics equations, or logic.",
    func=python_repl.run,
)
tools = [wikipedia, python_tool]

# --- 4. THE LANGCHAIN AGENT ---
memory = InMemorySaver()
system_prompt = "You are FRIDAY, a superhuman scientist assistant. You are analytical, brilliant, and concise. You MUST use your tools to accurately answer questions or execute calculations."

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory
)
config = {"configurable": {"thread_id": "friday_session_1"}}

speak("Systems online. Good morning.")

# --- 5. THE MAIN VOICE LOOP ---
while True:
    accumulated_input = ""
    
    while True:
        chunk = listen()
        
        if not chunk:
            continue
            
        if "exit" in chunk.lower() or "quit" in chunk.lower():
            speak("Shutting down core processors. Goodbye.")
            exit()
        
        accumulated_input += chunk + ". "
        console.print(f"[dim yellow]Drafting query: {accumulated_input}[/dim yellow]")
        
        time.sleep(1)
        
        engine.say("Are you done speaking?")
        engine.runAndWait()
        
        confirmation = listen()
        
        if confirmation:
            conf_lower = confirmation.lower()
            if any(word in conf_lower for word in ["yes", "yeah", "done", "yep", "proceed", "i am done"]):
                break 
            
            elif any(word in conf_lower for word in ["no", "not yet", "wait", "hold on"]):
                engine.say("Okay, go ahead. I am listening.")
                engine.runAndWait()
                continue 
            
            else:
                engine.say("I didn't catch a clear yes or no, but I will process what I have.")
                engine.runAndWait()
                break
        else:
            engine.say("I didn't hear a confirmation. Processing now.")
            engine.runAndWait()
            break
            
    user_input = accumulated_input.strip()
    
    if not user_input:
        continue
        
    console.print("\n[bold cyan blink]FRIDAY is compiling data...[/bold cyan blink]")
    engine.say(random.choice(["Processing.", "Right away.", "Calculating.", "Just a moment."]))
    engine.runAndWait()
    
    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
        )
        final_answer = response["messages"][-1].content
        speak(final_answer)
        
    except Exception as e:
        console.print(f"[bold red]CRITICAL ERROR:[/bold red] {e}")
        speak("I encountered a system failure while processing that request.")