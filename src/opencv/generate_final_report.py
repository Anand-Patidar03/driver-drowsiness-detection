import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

doc = docx.Document()

# Styles
style = doc.styles['Normal']
font = style.font
font.name = 'Arial'
font.size = Pt(11)

# Title
title = doc.add_heading('Project Report: Driver Drowsiness Monitoring System', 0)
title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

doc.add_paragraph('\n')

# Section: Project Overview (Why, What, How, Future Uses)
doc.add_heading('1. Project Overview', level=1)

# Why
doc.add_heading('Why we chose this project:', level=2)
p_why = doc.add_paragraph('Road accidents caused by driver fatigue and micro-sleeps are a major public safety issue, leading to thousands of fatalities and injuries each year globally. We chose this project because it presents a practical opportunity to apply modern Artificial Intelligence and Computer Vision techniques to a real-world problem, potentially saving lives by actively preventing these accidents.')

# What
doc.add_heading('What problem this project solves:', level=2)
p_what = doc.add_paragraph('The project addresses the critical issue of detecting when a driver is falling asleep at the wheel. It removes the need for expensive, invasive physical sensors (like EEG monitors attached to the driver) and instead provides a passive, non-intrusive monitoring solution using standard camera hardware.')

# How
doc.add_heading('How it solves that problem:', level=2)
p_how = doc.add_paragraph('The system continuously monitors the driver using a standard webcam feed. It operates via a three-stage pipeline:\n'
'1. Computer Vision Module: Utilizes OpenCV and Haar Cascades to reliably detect the driver\'s face and subsequently isolate and track the left and right eyes in real-time.\n'
'2. Deep Learning Classification: Feeds the dynamically cropped eye regions into a custom Convolutional Neural Network (CNN). The CNN evaluates the image and classifies the eye state as either Open or Closed.\n'
'3. State Logic & Dashboard: Tracks the eye-states over time. A state-machine logic differentiates between normal physiological blinking and prolonged eye closure indicative of drowsiness. Once a configurable threshold is breached, a Streamlit dashboard triggers an active alarm state.')

# More Uses
doc.add_heading('What can be more uses of this project:', level=2)
p_more = doc.add_paragraph('Beyond automotive safety, this technology can be adapted for:\n'
'• Heavy machinery and crane operators to prevent workplace accidents.\n'
'• Railway engineers and train conductors during long overnight routes.\n'
'• Pilot fatigue monitoring in commercial aircraft cockpits.\n'
'• Checking student attentiveness in remote-learning or online exam environments.\n'
'• General occupational health monitoring for desk workers experiencing extreme screen fatigue.')

doc.add_page_break()

# Section: Progress and Completion Status
doc.add_heading('2. Current Completion Status', level=1)

# Partner 1
doc.add_heading('Module 1: Computer Vision & Localization (Student 1)', level=2)
doc.add_paragraph('Status: COMPLETED', style='Intense Quote')
p1_comp = doc.add_paragraph('Tasks Finished:', style='List Bullet')
p1_comp = doc.add_paragraph('• Initialized project environment and resolved OpenCV/MediaPipe dependency pipelines.', style='List Bullet')
p1_comp = doc.add_paragraph('• Developed the core FaceDetector script to extract the facial bounding box using Haar cascades.', style='List Bullet')
p1_comp = doc.add_paragraph('• Implemented the EyeDetector module, which computes ROIs localized strictly to the upper 60% of the face to eliminate false positives (e.g., tracking nostrils/mouth).', style='List Bullet')
p1_comp = doc.add_paragraph('• Successfully mapped isolated eye bounding boxes dynamically onto the live video feed.', style='List Bullet')
p1_rem = doc.add_paragraph('Pending Tasks: Directly formatting the cropped eye output tensors to feed into the CNN inference engine.', style='List Bullet')

# Partner 2
doc.add_heading('Module 2: Dashboard UI & Logic Integration (Roll No.: 24UEC250)', level=2)
doc.add_paragraph('Status: COMPLETED', style='Intense Quote')
p2_comp = doc.add_paragraph('Tasks Finished:', style='List Bullet')
p2_comp = doc.add_paragraph('• Built a modular Streamlit dashboard interface to display eye status, driver status, and system metrics.', style='List Bullet')
p2_comp = doc.add_paragraph('• Implemented temporal drowsiness detection logic to differentiate normal blinking from drowsiness using continuous closure timers and configurable thresholds.', style='List Bullet')
p2_comp = doc.add_paragraph('• Added edge-case handling for "No Face Detected" and "Eye Not Detected" to ensure temporary tracking loss does not trigger false drowsiness alarms.', style='List Bullet')
p2_comp = doc.add_paragraph('• Validated the logic with mock input data simulating rapid blinking, prolonged closure, and single-eye closure.', style='List Bullet')
p2_rem = doc.add_paragraph('Pending Tasks: Final pipeline connection mapping real-time webcam data and ML evaluation to the finalized dashboard alerts.', style='List Bullet')

# Partner 3
doc.add_heading('Module 3: ML/CNN Eye-State Classification (Anand)', level=2)
doc.add_paragraph('Status: COMPLETED', style='Intense Quote')
p3_comp = doc.add_paragraph('Tasks Finished:', style='List Bullet')
p3_comp = doc.add_paragraph('• Processed the MRL Eye Dataset, utilizing a subject-independent Train/Validation/Test split to avoid data leakage.', style='List Bullet')
p3_comp = doc.add_paragraph('• Standardized image preprocessing pipelines (converted to grayscale, resized to 80x80, normalized 0-1) and stored as efficient .npz structures.', style='List Bullet')
p3_comp = doc.add_paragraph('• Designed and trained an end-to-end CNN featuring three convolutional layers (32, 64, 128 filters), max-pooling, dense layers with dropout, and a sigmoid binary classifier.', style='List Bullet')
p3_comp = doc.add_paragraph('• Achieved an 87.63% test accuracy baseline and saved model weights as drowsiness_cnn_model.keras.', style='List Bullet')
p3_rem = doc.add_paragraph('Pending Tasks: Improve recall specifically for the closed-eye class (currently lower than open-eye recall) via balancing or augmentation, as classifying closed eyes is the critical success vector for this system.', style='List Bullet')

doc.add_paragraph('\n')

# Section: Future Scopes
doc.add_heading('3. Future Scope of Improvement', level=1)
p_future = doc.add_paragraph('To make this project more effective and robust in the future, the following improvements can be explored:')
p_f1 = doc.add_paragraph('• Infrared (IR) Camera Integration: Standard webcams fail in low-light conditions (e.g., night-time driving). Modifying the CV module to accept IR video feeds would allow 24/7 monitoring.', style='List Bullet')
p_f2 = doc.add_paragraph('• Head Pose & Yawn Expansion: Extending the ML architecture to detect yawning frequencies and track head-pose estimation (driver looking away from the road for extended periods) for a more comprehensive fatigue profile.', style='List Bullet')
p_f3 = doc.add_paragraph('• Temporal Models (RNN/LSTM): Upgrading the simple state-machine temporal threshold to an LSTM model that can interpret historical patterns of blink frequencies over hours to predict fatigue before a micro-sleep even occurs.', style='List Bullet')
p_f4 = doc.add_paragraph('• Edge Deployment: Compiling and optimizing the CNN using TensorFlow Lite or TensorRT for deployment on low-powered edge devices (like Raspberry Pi) directly embedded into vehicle dashboards.', style='List Bullet')

doc.save('Final_Project_Report.docx')
print('Report generated successfully: Final_Project_Report.docx')
