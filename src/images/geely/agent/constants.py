import os
import sys
import socket

TYPE_COMFYUI = 'comfyui'
TYPE_SD = 'sd'
BACKEND_TYPE = os.getenv('BACKEND_TYPE', TYPE_COMFYUI)

WORK_DIR = os.getenv('WORK_DIR', '/root')
MNT_DIR = os.getenv('MODEL_ASSET_DIR', '/mnt/auto')
VENV_DIR = os.getenv('VENV_DIR', WORK_DIR + '/venv')
SNAPSHOT_DIR = MNT_DIR + '/snapshots'
SNAPSHOT_PATTERN = '%Y%m%d-%H%M%S'
COMFYUI_DIR = os.getenv('COMFYUI_DIR', WORK_DIR + '/comfyui')
COMFYUI_PROCESS_PORT = 8188
COMFYUI_BOOT_CMD = [
    f"{VENV_DIR}/bin/python",
    f"{COMFYUI_DIR}/main.py",
    "--listen",
    "0.0.0.0",
    "--input-directory",
    f"{MNT_DIR}/input",
    "--output-directory",
    f"{MNT_DIR}/output",
    "--temp-directory",
    f"{MNT_DIR}/output"
]

SD_DIR = os.getenv('SD_DIR', WORK_DIR + '/stable-diffusion-webui')
SD_PROCESS_PORT = 7860
SD_BOOT_CMD = [
    f"{VENV_DIR}/bin/python",
    f"{SD_DIR}/webui.py",
    "--listen",
    "--xformers",
    "--enable-insecure-extension-access",
    "--skip-version-check",
    "--no-download-sd-model",
    "--gradio-allowed-path=/"
]
# if BACKEND_TYPE == TYPE_COMFYUI:
#     BACKEND_PROCESS_PORT = COMFYUI_PROCESS_PORT
#     BOOT_CMD = COMFYUI_BOOT_CMD
# else:
#     BACKEND_PROCESS_PORT = SD_PROCESS_PORT
#     BOOT_CMD = SD_BOOT_CMD

BOOT_CMD = sys.argv[1:]
BACKEND_PROCESS_PORT = 9001

print("boot cmd", BOOT_CMD)

APP_HOST = f"127.0.0.1:{BACKEND_PROCESS_PORT}"

DEFAULT_READINESS_POLL_INTERVAL = 3
DEFAULT_READINESS_TIMEOUT = 300
DEFAULT_LIVENESS_POLL_INTERVAL = 5

# API Mode
AUTO_LAUNCH_SNAPSHOT_NAME = os.getenv("AUTO_LAUNCH_SNAPSHOT_NAME", "latest")
# TODO 提供快照轮转机制，环境变量可配置未使用的快照上限，生产环境使用的快照需保证不会被轮转

# OSS
HEADER_KEY_ACCESS_KEY_ID = "x-fc-access-key-id"
HEADER_KEY_ACCESS_KEY_SECRET = "x-fc-access-key-secret"
HEADER_KEY_SECURITY_TOKEN = "x-fc-security-token"
ALIBABA_CLOUD_ACCESS_KEY_ID = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "")
ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "")
ALIBABA_CLOUD_SECURITY_TOKEN = os.getenv("ALIBABA_CLOUD_SECURITY_TOKEN", "")
OSS_BUCKET_DOMAIN = os.getenv("OSS_BUCKET_DOMAIN", "")
OSS_KEY_PREFIX = os.getenv("OSS_KEY_PREFIX", "comfyui_serverless_api")
OSS_EXPIRES_IN_SECOND = os.getenv("OSS_EXPIRES_IN_SECOND", "")
OSS_OUTPUT_DOMAIN = os.getenv("OSS_OUTPUT_DOMAIN", "")
INSTANCE_ID = os.getenv("FC_INSTANCE_ID", socket.gethostname())

PREWARM_PROMPT = os.getenv("PREWARM_PROMPT", "")
