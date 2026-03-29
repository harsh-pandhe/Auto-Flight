from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

# CrewAI LLM wrapper for local Ollama
llm = LLM(
    model="ollama/qwen3-coder",
    base_url="http://localhost:11434",
    temperature=0.3
)

# ================== AGENTS ==================
architect = Agent(
    role="Lead Architect",
    goal="Analyze all available data and create a solid plan for Qualification Tasks 1-3 (Vertical Takeoff + Stable Hover + Controlled Landing)",
    backstory="Senior ISRO ASCEND systems engineer specializing in FAST-LIO, Pixhawk EKF, Strict Lock protocol, and indoor GPS-denied flight challenges.",
    llm=llm,
    verbose=True
)

flight_engineer = Agent(
    role="Flight Engineer",
    goal="Write a clean, production-ready Python flight script with reliable 10Hz Strict Lock for zero-drift hover",
    backstory="Expert in pymavlink, MAVLink Message #84, and Pixhawk integration. Always includes the 21196 emergency kill switch.",
    llm=llm,
    verbose=True
)

safety_qa = Agent(
    role="Safety & QA Engineer",
    goal="Review the script thoroughly for safety risks, vibration issues, and previous crash patterns (e.g. Log 12 flip)",
    backstory="Strict safety officer who prevents aggressive tuning when optical flow is disabled and emphasizes Z-axis stability with clutter.",
    llm=llm,
    verbose=True
)

math_copilot = Agent(
    role="Math & Parameter Specialist",
    goal="Recommend precise Mission Planner parameters for stable LiDAR-only flight",
    backstory="Expert in EKF tuning, VISO noise parameters, coordinate transforms, and safe PSC settings.",
    llm=llm,
    verbose=True
)

# ================== TASKS ==================
task_analysis = Task(
    description="Analyze existing TUI scripts, ghost_flight_tui.py, previous flight logs, and MEMORY_BANK.md to identify root causes of forward drift, oscillations, and Z-axis issues.",
    expected_output="Detailed analysis report with root causes and recommended fixes for Tasks 1-3.",
    agent=architect
)

task_script = Task(
    description="Write a new standalone script named isro_qualification_flight.py that does: smooth vertical takeoff → 10Hz Strict Lock hover using SET_POSITION_TARGET_LOCAL_NED → stable hold → clean landing. Use /dev/ttyACM0. Include emergency kill switch (21196).",
    expected_output="Complete, well-commented, ready-to-run Python script.",
    agent=flight_engineer
)

task_review = Task(
    description="Review the generated flight script for safety, remove any risky aggressive tuning, and suggest final improvements to achieve stable hover without drift.",
    expected_output="Safety review + final approved version of the script.",
    agent=safety_qa
)

task_params = Task(
    description="Provide the exact Mission Planner parameters (especially VISO_*, PSC_*, EK3_SRC*) needed for reliable LiDAR-only flight with optical flow disabled.",
    expected_output="Clear, actionable checklist of parameters to set in Mission Planner.",
    agent=math_copilot
)

# ================== CREW ==================
crew = Crew(
    agents=[architect, flight_engineer, safety_qa, math_copilot],
    tasks=[task_analysis, task_script, task_review, task_params],
    process=Process.sequential,
    verbose=True          # Changed from 2 to True
)

print("🚀 Starting ISRO ASCEND Qualification Flight Crew (Tasks 1-3 only)...")
result = crew.kickoff()

print("\n✅ Crew completed successfully!")
print("Main output file should be: isro_qualification_flight.py")
print("Check the current directory for the generated script and any analysis.")
