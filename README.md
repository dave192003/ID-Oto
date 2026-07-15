# ID_Oto
<img width="1900" height="358" alt="image" src="https://github.com/user-attachments/assets/3c6b9d0d-365c-4a8a-81ac-9591f7b5a83e" />



## Overview

**ID-Oto** is an **n8n automation workflow** designed to automate the processing of ID photos, reducing manual editing time and  the preparation of print-ready ID pictures.

## Automation Process

**Step-by-step workflow:**

1. **Upload Image/Photo**

   * User uploads the raw image or photo on website and choose the size of an id.

2. **Background Removal**

   * The system automatically removes the background from the uploaded photo.

3. **Photo Enhancement**

   * The image quality is enhanced for better clarity, lighting, and overall appearance.

4. **Crop to Designated Size**

   * The photo is automatically cropped according to the required ID dimensions.

5. **Layout for Printing**

   * Multiple copies of the processed ID photo are arranged into a printable sheet layout.

6. **Print Ready Output**

   * Final output is generated and prepared for printing.

# Prerequisite
Before running the project, install the following:

- Docker Desktop: https://www.docker.com/products/docker-desktop/

# N8N WORKFLOW
-Attached file below is the n8n workflow. <br>
[ID-Oto N8N Workflow](<../ID-Oto Workflow.json>)<br>

## Steps to import ID-Oto workflow on N8N
-Open your n8n instance in your browser. <br>
-From the dashboard, click Create Workflow (or open an existing workspace). <br>
-In the workflow editor, click the ⋮ (three-dot menu) or Workflow menu (depending on your n8n version). <br>
<img width="439" height="129" alt="Screenshot 2026-07-15 201530" src="https://github.com/user-attachments/assets/6cb91020-2610-4ecd-a34c-2056d8915caf" />


-Select Import from File. <br>
<img width="349" height="322" alt="Screenshot 2026-07-15 202013" src="https://github.com/user-attachments/assets/955d7a00-e205-4c9d-9202-9e368028ba5e" />

-Browse to and select your .json workflow file. <br>
-Click Open. <br>
-The workflow will be loaded into the editor. <br>
-Click Save to save the imported workflow. 

