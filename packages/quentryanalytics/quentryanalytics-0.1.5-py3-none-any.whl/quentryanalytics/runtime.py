import docker

def run_for_google_colab() -> None:
    client = docker.from_env()
    image_name = "us-docker.pkg.dev/colab-images/public/runtime:latest"

    # Create a container with port mappings
    container = client.containers.run(
        image=image_name,
        ports={"127.0.0.1:9000", "8000"},
        detach=False
    )

    container.exec_run(f"pip install quentryanalytics")
    print("quentryanalytics package installed.")
