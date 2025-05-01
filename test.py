import base64
import httpx

def test_run_prediction():
    """Тестирует распознавание схемы по PDF"""
    with open(r"C:\Users\usiko\Desktop\Схемы pdf\01\01_01.pdf", "rb") as pdf_file:
        pdf_data = pdf_file.read()
        base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
        data_url = f"data:application/pdf;base64,{base64_pdf}"

    payload = {
        "circuit_data": data_url
    }

    response = httpx.post(
        "http://localhost:8001/api/predict/run_prediction",
        json=payload,
        timeout=30.0
    )

    print("Status code (run_prediction):", response.status_code)
    if response.status_code == 200:
        print("Response JSON:", response.json())
    else:
        print("Error:", response.text)


def test_run_clusterization():
    """Тестирует кластеризацию извлечённых компонентов"""
    response = httpx.post(
        "http://localhost:8002/api/cluster/run_clusterization",
        timeout=30.0
    )

    print("Status code (run_clusterization):", response.status_code)
    if response.status_code == 200:
        clusters = response.json()
        print("Clusterization result:")
        for cluster in clusters["clusters"]:
            print(f"- Cluster {cluster['id']} ({cluster['name']}), label={cluster['label']}")
            print(f"  Components: {len(cluster['components'])}")
    else:
        print("Error:", response.text)


if __name__ == "__main__":
    test_run_prediction()
    #test_run_clusterization()
