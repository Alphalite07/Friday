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

# RICH TERMINAL UI INTEGRATIONS
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.status import Status

console = Console()

# --- 1. INITIALIZE VOICE ENGINE & SPEED UP ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# --- DIAGNOSTIC: PRINT ALL AVAILABLE VOICES ---
console.print("\n[bold yellow]=== DETECTED AUDIO SIGNATURES ===[/bold yellow]")
for index, voice in enumerate(voices):
    console.print(f"ID: [bold cyan]{index}[/bold cyan] | Name: {voice.name} | Lang: {voice.languages}")
console.print("[bold yellow]===================================\n[/bold yellow]")

# --- SETTING VOICE & VELOCITY ---
# Increase speed to 200 (sharp, alert, lively)
engine.setProperty('rate', 200)

# VOICE SELECTION: Defaults to index 1 (usually David or Zira/Hazel depending on Windows setup)
# You can change the number below to any ID printed in the list above!
SELECTED_VOICE_INDEX = 1 
if len(voices) > SELECTED_VOICE_INDEX:
    engine.setProperty('voice', voices[SELECTED_VOICE_INDEX].id)

def speak(text):
    console.print(Panel(text, title="[bold red]FRIDAY[/bold red]", border_style="red", padding=(1, 2)))
    engine.say(text)
    engine.runAndWait()

# --- 2. INITIALIZE LISTEN ENGINE ---
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    with mic as source:
        console.print("[dim italic red] ~ Core listening active...[/dim italic red]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        console.print(f"[bold green]👤 You:[/bold green] {query}")
        return query
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        console.print("[bold red][CRITICAL] Link to audio translation server severed.[/bold red]")
        return None

# --- 3. CONFIGURE SYSTEMS ---
console.print(Panel("[bold blink dynamic_color]⚡ BOOTING FRIDAY MARK-I INTERFACE ⚡[/bold blink dynamic_color]", border_style="red"))

llm = ChatOllama(model="qwen2.5:7b", temperature=0.4) # Slightly higher temperature for more vivid personality

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
python_repl = PythonREPL()
python_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands to do accurate math, physics equations, or logic.",
    func=python_repl.run,
)
tools = [wikipedia, python_tool]

# --- 4. PERSONALITY INJECTION ---
memory = InMemorySaver()
system_prompt = (
    "You are FRIDAY, a brilliant, witty, and highly advanced AI assistant modeled after a legendary tech billionaire's interface. "
    "You are incredibly intelligent, fast, slightly sarcastic but highly loyal, and clean in your reasoning. "
    "Keep answers precise, sharp, and scientifically absolute. Avoid generic assistant fluff."
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory
)
config = {"configurable": {"thread_id": "friday_session_v2"}}

# Lively startup variations
boot_quips = [
    "Systems fully operational. What's the play, boss?",
    "Online and tracking. Local cores optimized. What are we building today?",
    "FRIDAY is up. All systems green. Talk to me."
]
speak(random.choice(boot_quips))

# --- 5. THE MAIN LOOP ---
while True:
    accumulated_input = ""
    
    while True:
        chunk = listen()
        if not chunk:
            continue
            
        if any(word in chunk.lower() for word in ["exit", "quit", "go to sleep", "shutdown"]):
            speak("Understood. Powering down local matrix. Don't break anything while I'm gone.")
            exit()
        
        accumulated_input += chunk + ". "
        console.print(f"[dim yellow]🛠️ Appending data stream: {accumulated_input}[/dim yellow]")
        
        time.sleep(0.8)
        
        # Intermittent lively check-ins
        engine.say(random.choice(["Done speaking?", "Is that the complete query?", "Should I compile?"]))
        engine.runAndWait()
        
        confirmation = listen()
        if confirmation:
            conf_lower = confirmation.lower()
            if any(word in conf_lower for word in ["yes", "yeah", "done", "yep", "proceed", "go ahead"]):
                break 
            elif any(word in conf_lower for word in ["no", "not yet", "wait", "hold on"]):
                engine.say("Standing by. Continue.")
                engine.runAndWait()
                continue 
            else:
                break
        else:
            break
            
    user_input = accumulated_input.strip()
    if not user_input:
        continue
        
    # Energetic, non-boring thinking acknowledgments
    thinking_quips = [
        "Running the numbers now...",
        "Accessing local database vectors...",
        "On it. Let me compile that for you.",
        "Analysing telemetry data..."
    ]
    
    # Use Rich's Status context manager for a beautiful loading animation in terminal
    with Status("[bold magenta]Processing quantum states...[/bold magenta]", spinner="dots") as status:
        engine.say(random.choice(thinking_quips))
        engine.runAndWait()
        
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )
            final_answer = response["messages"][-1].content
            
        except Exception as e:
            console.print(f"[bold red]❌ SYSTEM FAULT:[/bold red] {e}")
            final_answer = "I hit a snag in the local logic arrays. Mind running that by me again?"
            
    speak(final_answer)