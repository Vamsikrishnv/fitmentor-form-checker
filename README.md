\# FitMentor AI - Form Checker (Alpha v0.1)



An AI-powered fitness coach that checks your workout form in real-time using computer vision.



\## 🎯 Current Features



\### Working Exercises:

\- ✅ \*\*Squat\*\* - Depth \& knee tracking analysis

\- ✅ \*\*Push-up\*\* - Rep counter with body alignment check

\- ✅ \*\*Plank\*\* - Hold timer with form monitoring

\- ✅ \*\*Lunge\*\* - Front/back leg angle analysis

\- ✅ \*\*Deadlift\*\* - Back safety monitor (critical for injury prevention)



\### Technology:

\- Real-time pose detection (MediaPipe)

\- Angle calculation \& biomechanics analysis

\- Form scoring (0-100)

\- Color-coded feedback (green/yellow/red)



\## 🚧 Alpha Status - Known Issues



This is an early prototype. Tracking needs significant improvement:



\*\*General Issues:\*\*

\- Angle detection needs smoothing/filtering

\- Rep counting can be inconsistent

\- Works best from specific camera angles

\- No calibration for different body types



\*\*Specific Exercise Issues:\*\*

\- \*\*Squat:\*\* Best from direct side view, sometimes false counts

\- \*\*Push-up:\*\* Position detection oversensitive

\- \*\*Plank:\*\* Timer can be inconsistent

\- \*\*Lunge:\*\* Struggles detecting front vs back leg

\- \*\*Deadlift:\*\* Back angle needs refinement



\## 🎯 Improvement Roadmap



Week 2 Focus:

\- \[ ] Add angle smoothing/filtering

\- \[ ] Improve rep counting logic with state machines

\- \[ ] Add confidence thresholds

\- \[ ] Better "ready position" detection

\- \[ ] Calibration for body dimensions



Future:

\- \[ ] Support multiple camera angles

\- \[ ] Add more exercises

\- \[ ] Mobile app

\- \[ ] Personal AI coach (LLM integration)



\## 🛠️ Setup

```bash

\# Clone repo

git clone https://github.com/Vamsikrishnv/fitmentor-form-checker.git

cd fitmentor-form-checker



\# Create virtual environment

python -m venv venv

source venv/bin/activate  # Windows: venv\\Scripts\\activate



\# Install dependencies

pip install -r requirements.txt

```



\## 🏃 Run

```bash

\# Test individual exercises:

python squat\_checker.py

python pushup\_checker.py

python plank\_checker.py

python lunge\_checker.py

python deadlift\_checker.py

```



Press 'q' to quit any exercise.



\## 📊 Day-by-Day Progress



\- \*\*Day 1:\*\* Basic pose detection + webcam setup ✅

\- \*\*Day 2:\*\* 5 exercise analyzers with angle calculations ✅

\- \*\*Day 3:\*\* Coming tomorrow - Bug fixes + improvements



\## 🤝 Contributing



This is a learning project built in public! 



Known issues are documented above. PRs welcome, especially for:

\- Angle smoothing algorithms

\- Better rep counting logic

\- Additional exercises



\## 📝 License



MIT



\## 🔗 Building in Public



Follow the journey: \[Your Twitter/X handle]



---



\*\*Status:\*\* Alpha v0.1 - Working prototype with known tracking issues

\*\*Last Updated:\*\* November 5, 2025

