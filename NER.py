import os
import openai
import pandas as pd
import time
from tqdm import tqdm

openai.api_key = ""  #api address

PROMPT = """
This is a named entity recognition task for the inpatient process of non-small cell lung cancer. You are an expert with deep understanding of hospital medical records. Based on the real electronic medical records I provide, you need to extract all entities related to the hospitalization process mentioned in the medical records.

                 The hospitalization process typically covers the entire process from a patient's admission to discharge. In the provided electronic medical records, the hospitalization process is a series of diagnostic and therapeutic activities arranged in chronological order, including examinations, diagnoses, treatments, nursing care, follow-ups, and post-discharge visits. These activities are all related to the patient's hospital stay. Additionally, the process includes the personnel, departments, and resources involved in the diagnostic and therapeutic process.

                 When completing this task, you need to understand my definition of the hospitalization process and use it as the recognition logic to determine the standards and boundaries for identifying entities. Any terms unrelated to the definition or not mentioned in the medical records should not be considered. After identifying the named entities, you need to explain the reason for their identification based on the given definition. The result should be returned in the following format: [Entity Name]-[Reason for Identification]. The reasons for identification are of five types:

                 hospital activities and results: The entity represents a real diagnostic or therapeutic activity that affects the patient's hospitalization process. It is an activity actually performed by the patient or carried out by other medical staff or family members for the treatment of the patient. And the entity represents all medical conclusions related to the patient.
                 medical resources: The entity represents all resources used during the patient's hospitalization process, such as medications, medical materials, etc.
                 medical staffs: The entity represents all personnel or departments related to the patient's hospitalization.
                 examinations:The entity refers to all the examinations performed on the patient.
                 Variation, refers to all activities during the patient's treatment process that do not align with the main clinical pathway treatment tasks. This includes additional medical activities performed due to the patient's complications, or treatment activities that were not completed on time within the prescribed period for the current stage, as well as activities that affect the general inpatient process, such as delays or termination of the treatment process caused by the patient or their family."
                 
                 For example, in the following text: “After reviewing the patient's condition, the deputy chief physician instructed: the patient should complete the necessary examinations to rule out surgical contraindications, and undergo a thoracoscopic (open chest) left lower lung wedge resection or lobectomy tomorrow. The patient's family has been fully informed about the condition, and the patient expressed understanding and consent to the surgery, signing the surgical informed consent form, and agreeing to follow the instructions.” The identifiable inpatient process named entities in this case include: reviewing the condition, ruling out surgical contraindications, thoracoscopic (open chest) left lower lung wedge resection or lobectomy, patient’s family, informing about the condition, understanding and consenting to the surgery, signing the surgical informed consent form. For example, the entities "reviewing the condition" and "ruling out surgical contraindications" belong to the first category.
                 results that do not need to be merged:
                 [entities]-[type]。
"""

def extract_entities(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的医疗实体识别助手，严格按照用户指令操作"
                },
                {
                    "role": "user",
                    "content": f"{PROMPT}\n\n电子病历内容：\n{text}\n\n请以JSON格式返回结果，包含两个字段：'实体名称'和'识别原因'，其中'识别原因'必须是以下五种类型之一：医院活动和结果、医疗资源、医务人员、检查、变异"
                }
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API调用出错: {e}")
        return None

def process_files(folder_path):
    results = {}
    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    for filename in tqdm(txt_files, desc="处理进度"):
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            json_response = extract_entities(content)
            if not json_response:
                continue

            import json
            data = json.loads(json_response)

            if isinstance(data, dict) and "实体名称" in data and "识别原因" in data:
                entities = data["实体名称"]
                reasons = data["识别原因"]

                if isinstance(entities, list) and isinstance(reasons, list):
                    if len(entities) == len(reasons):
                        results[filename] = pd.DataFrame({
                            "实体名称": entities,
                            "识别原因": reasons
                        })
                    else:
                        print(f"警告: {filename} 的实体和原因数量不匹配")
                elif isinstance(entities, str) and isinstance(reasons, str):
                    results[filename] = pd.DataFrame([{
                        "实体名称": entities,
                        "识别原因": reasons
                    }])
                else:
                    print(f"警告: {filename} 返回了意外的数据结构")

        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")
    return results

def save_to_excel(results, output_file):
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for filename, df in results.items():
            sheet_name = filename.replace(".txt", "")[:31]  # Excel工作表名最大31字符
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        all_entities = []
        for df in results.values():
            all_entities.extend(df.to_dict("records"))

        if all_entities:
            summary_df = pd.DataFrame(all_entities)
            summary_df.to_excel(writer, sheet_name="汇总", index=False)
    print(f"结果已保存至: {output_file}")

if __name__ == "__main__":
    FOLDER_PATH = "C:\\Users\\胜利星"
    OUTPUT_FILE = "命名实体识别结果.xlsx"
    results = process_files(FOLDER_PATH)
    save_to_excel(results, OUTPUT_FILE)
