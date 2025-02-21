import os
import openai
from time import sleep

# 初始化设置
openai.api_key = "xxx"
INPUT_DIR = "input_docs path"
OUTPUT_DIR = "output_docs path"
MODEL_NAME = "gpt-4"


def ner_extraction(text):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": f"""
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
                 [entities]-[type]
                 Specific text:{text}"""
            }],
            temperature=0.1,
            max_tokens=4096,
            presence_penalty=0
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"API调用出错: {str(e)}")
        return ""


def process_document(file_path, output_dir):
    """处理单个文档"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = [s.strip() for s in content.split('---page break---') if s.strip()]

    results = []
    for idx, section in enumerate(sections, 1):
        print(f"正在处理第 {idx}/{len(sections)} 部分...")
        result = ner_extraction(section)
        results.append(f"=== 第 {idx} 部分抽取结果 ===\n{result}\n")
        sleep(1)

    return results


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".txt"):
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, f"NER_{filename}")

        print(f"\n正在处理文件: {filename}")
        results = process_document(input_path, OUTPUT_DIR)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(results))
        print(f"已保存结果到: {output_path}")


if __name__ == "__main__":
    main()