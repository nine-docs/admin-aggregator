from langchain.prompts import PromptTemplate,FewShotPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import pandas as pd
import requests,json,tqdm,os,argparse

def set_openai_api_key(api_key: str):
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = api_key

def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    document = loader.load()
    return document

def split_text(document):
    # 문서 분할
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n\n",
        chunk_size=10000,
        chunk_overlap=500,
    )
    split_docs = text_splitter.split_documents(document)
    split_docs = split_docs[150:161]
    return split_docs

examples = [
    {
        "input": "Kubernetes provides you with: Service discovery and load balancing Kubernetes can expose a container using the DNS name or using their own IP address. If traffic to a container is high, Kubernetes is able to load balance and distribute the network traffic so that the deployment is stable. Storage orchestration Kubernetes allows you to automatically mount a storage system of your choice, such as local storages, public cloud providers, and more. Automated rollouts and rollbacks You can describe the desired state for your deployed containers using Kubernetes, and it can change the actual state to the desired state at a controlled rate. For example, you can automate Kubernetes to create new containers for your deployment, remove existing containers and adopt all their resources to the new container. Automatic bin packing You provide Kubernetes with a cluster of nodes that it can use to run containerized tasks. You tell Kubernetes how much CPU and memory (RAM) each container needs. Kubernetes can fit containers onto your nodes to make the best use of your resources. Self-healing Kubernetes restarts containers that fail, replaces containers, kills containers that don't respond to your user-defined health check, and doesn't advertise them to clients until they are ready to serve. Secret and configuration management Kubernetes lets you store and manage sensitive information, such as passwords, OAuth tokens, and SSH keys. You can deploy and update secrets and application configuration without rebuilding your container images, and without exposing secrets in your stack configuration. Batch execution In addition to services, Kubernetes can manage your batch and CI workloads, replacing containers that fail, if desired. Horizontal scaling Scale your application up and down with a simple command, with a UI, or automatically based on CPU usage. IPv4/IPv6 dual-stack Allocation of IPv4 and IPv6 addresses to Pods and Services Designed for extensibility Add features to your Kubernetes cluster without changing upstream source code. What Kubernetes is not Kubernetes is not a traditional, all-inclusive PaaS (Platform as a Service) system. Since Kubernetes operates at the container level rather than at the hardware level, it provides some generally applicable features common to PaaS offerings, such as deployment, scaling, load balancing, and lets users integrate their logging, monitoring, and alerting solutions. However, Kubernetes is not monolithic, and these default solutions are optional and pluggable. Kubernetes provides the building blocks for building developer platforms, but preserves user choice and flexibility where it is important. Kubernetes: Does not limit the types of applications supported. Kubernetes aims to support an extremely diverse variety of workloads, including stateless, stateful, and data-processing workloads. If an application can run in a container, it should run great on Kubernetes. Does not deploy source code and does not build your application. Continuous Integration, Delivery, and Deployment (CI/CD) workflows are determined by organization cultures and preferences as well as technical requirements. Does not provide application-level services, such as middleware (for example, message buses), data-processing frameworks (for example, Spark), databases (for example, MySQL), caches, nor cluster storage systems (for example, Ceph) as built-in services.",
        "question": "**질문:**\n\nKubernetes의 자동 복구(Self-healing) 기능은 무엇을 의미하는가?",
        "answer": "**답변:**\n\nKubernetes의 자동 복구(Self-healing) 기능은 컨테이너의 장애를 감지하고 이를 자동으로 복구하는 기능을 의미합니다. Kubernetes는 다음과 같은 방식으로 애플리케이션의 안정성을 보장합니다:\n\n- 실패한 컨테이너를 자동으로 재시작\n- 응답하지 않는 컨테이너를 종료하고 새로운 컨테이너로 교체\n- 사용자 정의된 헬스 체크(health check)에 실패한 컨테이너를 서비스에서 제거\n- 준비되지 않은(ready 상태가 아닌) 컨테이너는 트래픽을 받지 않도록 설정\n\n이러한 기능 덕분에 Kubernetes는 최소한의 개입으로도 애플리케이션의 가용성을 유지할 수 있습니다.\n\n**추가 설명:**\nKubernetes에서 `Liveness Probe`와 `Readiness Probe`를 활용하여 컨테이너의 상태를 지속적으로 모니터링할 수 있습니다.\n\n**예시 코드:**\n```yaml\napiVersion: v1\nkind: Pod\nmetadata:\n  name: example-pod\nspec:\n  containers:\n  - name: example-container\n    image: example-image:latest\n    livenessProbe:\n      httpGet:\n        path: /healthz\n        port: 8080\n      initialDelaySeconds: 3\n      periodSeconds: 5\n    readinessProbe:\n      httpGet:\n        path: /readiness\n        port: 8080\n      initialDelaySeconds: 3\n      periodSeconds: 5\n```\n위 설정에서는 `/healthz` 경로를 통해 컨테이너의 생존 여부를 확인하고, `/readiness` 경로를 통해 컨테이너가 요청을 받을 준비가 되었는지를 판단하여 트래픽을 분배할지 결정합니다."
    },
    {
        "input": "Pods with higher Priority can schedule on Nodes. Eviction is the process of proactively terminating one or more Pods on resource-starved Nodes. Cluster Administration Lower-level detail relevant to creating or administering a Kubernetes cluster. Windows in Kubernetes Kubernetes supports nodes that run Microsoft Windows. Extending Kubernetes Different ways to change the behavior of your Kubernetes cluster. Overview Kubernetes is a portable, extensible, open source platform for managing containerized workloads and services, that facilitates both declarative configuration and automation. It has a large, rapidly growing ecosystem. Kubernetes services, support, and tools are widely available. This page is an overview of Kubernetes. Kubernetes is a portable, extensible, open source platform for managing containerized workloads and services, that facilitates both declarative configuration and automation. It has a large, rapidly growing ecosystem. Kubernetes services, support, and tools are widely available. The name Kubernetes originates from Greek, meaning helmsman or pilot. K8s as an abbreviation results from counting the eight letters between the \"K\" and the \"s\". Google open-sourced the Kubernetes project in 2014. Kubernetes combines over 15 years of Google's experience running production workloads at scale with best-of-breed ideas and practices from the community. Going back in time Let's take a look at why Kubernetes is so useful by going back in time. Deployment evolution Traditional deployment era: Early on, organizations ran applications on physical servers. There was no way to define resource boundaries for applications in a physical server, and this caused resource allocation issues. For example, if multiple applications run on a physical server, there can be instances where one application would take up most of the resources, and as a result, the other applications would underperform. A solution for this would be to run each application on a different physical server. But this did not scale as resources were underutilized, and it was expensive for organizations to maintain many physical servers. Virtualized deployment era: As a solution, virtualization was introduced. It allows you to run multiple Virtual Machines (VMs) on a single physical server's CPU. Virtualization allows applications to be isolated between VMs and provides a level of security as the information of one application cannot be freely accessed by another application.",
        "question": "**질문:**\n\n물리 서버 기반 배포 방식에서 발생하는 주요 문제는 무엇인가?",
        "answer": "**답변:**\n\n물리 서버 기반 배포 방식에서는 애플리케이션 간 리소스 경합이 발생하여 특정 애플리케이션이 과도한 리소스를 차지할 수 있습니다. 또한, 각 애플리케이션을 개별 물리 서버에서 실행하는 방식은 리소스 활용도가 낮고 비용이 많이 듭니다.\n\n**추가 설명:**\n- 여러 애플리케이션이 동일한 서버에서 실행되면 리소스 경합이 발생하여 성능 저하가 발생할 수 있습니다.\n- 하나의 애플리케이션이 서버의 대부분의 리소스를 사용하면, 다른 애플리케이션의 성능이 저하됩니다.\n- 각 애플리케이션을 별도의 물리 서버에서 실행하는 경우, 서버 활용률이 낮고 하드웨어 비용이 증가합니다.\n\n**해결 방법:**\n이러한 문제를 해결하기 위해 가상화(Virtualization)가 도입되었습니다. 가상화를 사용하면 단일 물리 서버에서 여러 개의 가상 머신(VM)을 실행할 수 있으며, 애플리케이션 간의 격리와 보안성을 높일 수 있습니다.\n\n**예시:**\n```yaml\napiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: example-deployment\nspec:\n  replicas: 3\n  selector:\n    matchLabels:\n      app: example-app\n  template:\n    metadata:\n      labels:\n        app: example-app\n    spec:\n      containers:\n      - name: example-container\n        image: example-image:latest\n```\n위와 같이 Kubernetes의 Deployment를 활용하면 컨테이너화된 애플리케이션을 효율적으로 배포하고, 리소스를 최적화할 수 있습니다."
    }
    ,
    {
        "input": "Declarative object configuration retains changes made by other writers, even if the changes are not merged back to the object configuration file.",
        "question": "**질문:**\n\nDeclarative object configuration의 장점 중 하나는?",
        "answer": "**답변: **\n\nDeclarative object configuration의 주요 장점 중 하나는 '라이브 객체의 변경 사항이 유지된다'는 점입니다.**\n\n### 추가 설명\n- 선언적(Declarative) 방식에서는 `kubectl apply`를 사용하여 설정 파일을 기반으로 객체를 관리합니다.\n- 이를 통해 기존 객체의 일부가 변경되더라도 전체 객체를 교체하지 않고, 변경된 부분만 패치(Patch)됩니다.\n- 반면, 명령형(Imperative) 방식에서는 `kubectl replace` 같은 명령을 사용하여 전체 객체를 대체하므로, 변경 사항이 유지되지 않을 수 있습니다.\n\n### ✅ 예시 코드\n```sh\n# 기존 설정과의 차이를 확인\nkubectl diff -f configs/\n\n# 변경된 내용만 적용 (patch 방식)\nkubectl apply -f configs/\n```"
    }
    ,
    {
        "input": "For example, you can only have one Pod named myapp-1234 within the same namespace, but you can have one Pod and one Deployment that are each named myapp-1234.",
        "question": "**질문:**\n\nKubernetes에서 같은 이름을 가진 Pod와 Deployment를 동시에 생성할 수 있는 이유는?",
        "answer": "**답변: **\n\nKubernetes에서는 리소스 유형(Kind)이 다르면 같은 이름을 가질 수 있기 때문입니다.**\n\n### 추가 설명\n- 동일한 네임스페이스에서 **Pod와 Deployment**는 서로 다른 리소스 유형이므로 같은 이름을 가질 수 있습니다.\n- 하지만 같은 네임스페이스 내에서 같은 리소스 유형(Pod, Deployment 등)의 이름은 고유해야 합니다.\n- 네임스페이스를 다르게 설정하면 같은 이름의 객체를 여러 개 만들 수도 있습니다.\n- API 요청에서 개체를 식별할 때는 **네임스페이스 + 리소스 유형 + 이름**을 조합하여 관리합니다.\n\n### 예시 코드\n```sh\n# 동일한 네임스페이스에서 같은 이름을 가진 Pod와 Deployment 생성 가능\nkubectl create deployment myapp-1234 --image=nginx\nkubectl run myapp-1234 --image=nginx\n\n# 하지만 같은 네임스페이스에서 같은 이름의 Pod를 두 개 만들 수는 없음\nkubectl run myapp-1234 --image=nginx  # 에러 발생\n```\n\n** 해결 방법:**\n- 다른 네임스페이스를 사용하면 같은 이름을 가진 리소스를 만들 수 있습니다.\n```sh\nkubectl create namespace test-ns\nkubectl run myapp-1234 --image=nginx -n test-ns  # 성공\n```"
    }
]  

def generate_question(examples,split_docs):
    # 질문과 답변을 생성하는 프롬프트 템플릿
    example_prompt = PromptTemplate.from_template("input: {input} \n question: {question} \n answer: {answer}")

    # FewShotPromptTemplate 생성
    few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="""너는 기술 공식 문서를 기반으로 **핵심 개념**을 문제로 변환하는 AI야. 
        다음은 기술 공식 문서의 일부야:
     "**문서의 핵심 개념**에 기반한 **주관식 문제**를 1개 생성해줘. 
     문서에서 **실무에 유용한 정보**를 선별해서 질문을 생성하고, 그에 맞는 상세한 답변과 추가 정보를 제공해.
     문제는 실무에 도움이 되는 내용을 다루도록 해. 
     문제의 길이는 50자를 넘지 않도록 해.
     답안에는 반드시 **추가 설명**과 필요하다면 **예시 코드**을 포함해."
     답변은 **MD 형식**으로 만들어줘
     문제는 text 형태로 만들어줘
     ** 문제, 답변 형식 ** 을 반드시 통일해줘
     """,
    suffix="input:{input}",
    input_variables=["input"]
    )

    # LLM 모델 초기화 (예: OpenAI GPT)
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)

    # LLM Chain 생성
    chain = LLMChain(llm=llm, prompt=few_shot_prompt)

    # 결과를 저장할 리스트
    results = []

    # 각 문서 청크에 대해 질문과 답변 생성
    for doc in tqdm.tqdm(split_docs):
        input_text = doc.page_content  # 문서 청크의 텍스트
        response = chain.invoke(input=input_text)  # LLM에 전달하여 질문과 답변 생성
        
        # 결과를 딕셔너리로 저장
        result = {
            "input": input_text,
            "response": response
        }
        results.append(result)
    print("question generating succeed")
    return results
        
def parse_data(results):
    # 데이터 파싱
    parsed_data = []
    for item in results:
        question = item["response"]["text"].split("**답변:**")[0]
        question = question.replace("**질문:**\n\n","")
        answer = item["response"]["text"].split("**답변:**")[1]
        parsed_data.append({"Question": question, "Answer": answer})

    # DataFrame 생성
    df = pd.DataFrame(parsed_data)
    print("data parsing succeed")

    return df

def api_post(API_URL,df,category):
    # 요청 데이터 생성
    payload = [
        {
            "title": row["Question"],
            "contents": row["Answer"],
            "link": "null",
            "categoryTitle": category
        }
        for _, row in df.iterrows()
    ]

    # JSON 데이터 변환
    headers = {"Content-Type": "application/json"}
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload,ensure_ascii=False))
    print(response.text)
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set OpenAI API Key as an environment variable.")
    parser.add_argument("--api_key", required=True, help="Your OpenAI API Key")
    parser.add_argument("--file", required=True, help="Path to the PDF file")
    parser.add_argument("--url", required=True, help="Path to API URL")
    parser.add_argument("--category", required=True, help="category")

    args = parser.parse_args()
    set_openai_api_key(args.api_key)
    document = load_pdf(args.file)
    split_docs = split_text(document)
    results = generate_question(examples,split_docs)
    df = parse_data(results)
    response = api_post(args.url,df,args.category)
