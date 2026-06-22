import os
import time
import random
import sqlite3
import pyttsx3
import subprocess
from datetime import datetime
import speech_recognition as sr
import cv2
import psutil
import base64

# LANGCHAIN & AI CORE
from langchain_ollama import ChatOllama
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool, tool
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# PERMANENT MEMORY
from langgraph.checkpoint.sqlite import SqliteSaver

# RICH TERMINAL UI INTEGRATIONS
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.layout import Layout
from rich.table import Table
from rich import box

console = Console()

# --- 1. INITIALIZE VOICE ENGINE ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')

engine.setProperty('rate', 200)
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

# --- 3. EXTREMIS TOOLS (VISION, WEB, SYSTEM) ---
@tool
def get_system_time(query: str = "") -> str:
    """Returns the current precise date and time."""
    now = datetime.now()
    return f"The current system date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."

@tool
def open_application(app_name: str) -> str:
    """Opens a local application on the Windows machine."""
    app_name = app_name.lower().strip()
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "start chrome",
        "code": "code",
        "explorer": "explorer.exe",
        "spotify": "start spotify"
    }
    command = apps.get(app_name)
    if command:
        try:
            subprocess.Popen(command, shell=True)
            return f"Successfully initiated launch sequence for {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}. Error: {e}"
    return f"Application {app_name} not found in path."

@tool
def analyze_camera(query: str = "Describe what you see in detail.") -> str:
    """Captures a frame from the webcam and analyzes the physical world."""
    console.print("[bold blink red]Initializing optical sensors...[/bold blink red]")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return "Camera hardware failed to capture an image."
        
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    # Route image to the dedicated LLaVA vision model
    vision_llm = ChatOllama(model="llava", temperature=0.1)
    msg = HumanMessage(content=[
        {"type": "text", "text": query},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{jpg_as_text}"}}
    ])
    
    response = vision_llm.invoke([msg])
    return response.content

# Core Toolbelt Construction
web_search = DuckDuckGoSearchRun(name="web_search", description="Search the live internet for up-to-date information, news, or code documentation.")
python_repl = PythonREPL()
python_tool = Tool(
    name="python_repl",
    description="A Python shell to execute math, physics equations, or logic.",
    func=python_repl.run,
)

tools = [web_search, python_tool, get_system_time, open_application, analyze_camera]

# --- 4. CORE OS & PERMANENT MEMORY ---
def render_hud():
    """Generates a live system diagnostics panel."""
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    
    table = Table(box=box.SIMPLE_HEAVY, border_style="red")
    table.add_column("METRIC", style="dim red")
    table.add_column("STATUS", justify="right", style="bold red")
    table.add_row("CPU LOAD", f"{cpu}%")
    table.add_row("MEMORY", f"{ram}%")
    table.add_row("OPTICAL", "ONLINE")
    table.add_row("NETWORK", "SECURE")
    
    return Panel(table, title="[bold red]SYSTEM HUD[/bold red]", border_style="red", width=40)

console.print(Panel("[bold blink red]⚡ BOOTING FRIDAY EXTREMIS PROTOCOL ⚡[/bold blink red]", border_style="red"))
console.print(render_hud())

llm = ChatOllama(model="qwen2.5:7b", temperature=0.4)

system_prompt = (
    "You are FRIDAY, an omnipotent AI operating system with access to the live internet, local file execution, and physical optical cameras. "
    "If the user asks to see something, use your camera tool. If asked a current event, use your web search. "
    "Keep answers precise, sharp, and scientifically absolute. Maintain a witty, loyal personality."
)

db_path = "friday_memory.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory
)

config = {"configurable": {"thread_id": "anbu_core_profile"}}

speak(random.choice([
    "Systems fully operational. Welcome back, Anbu.",
    "Extremis protocol online. Optical, network, and memory arrays are green.",
    "I'm online. What are we building today?"
]))

# --- 5. THE MAIN VOICE LOOP ---
while True:
    accumulated_input = ""
    console.print("\n[bold red]🎙️ Listening...[/bold red]")
    
    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            try:
                audio = recognizer.listen(source, timeout=2.0, phrase_time_limit=10)
                chunk = recognizer.recognize_google(audio)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                break
            except sr.RequestError:
                console.print("[bold red][CRITICAL] Link to audio translation server severed.[/bold red]")
                break

        if chunk:
            if any(word in chunk.lower() for word in ["exit", "quit", "go to sleep", "shutdown"]):
                speak("Understood. Saving memory states and powering down local matrix.")
                conn.close()
                exit()
            
            accumulated_input += chunk + " "
            console.print(f"[dim red]🛠️ Data streamed: {chunk}[/dim red]")
            time.sleep(0.5)

    user_input = accumulated_input.strip()
    if not user_input:
        continue
        
    # Render HUD to update system metrics before she processes
    console.print(render_hud())
    
    with Status("[bold red]Processing quantum states...[/bold red]", spinner="dots") as status:
        engine.say(random.choice(["Running the numbers...", "Accessing tools...", "On it."]))
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