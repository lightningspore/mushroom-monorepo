from fastapi import FastAPI, Response
import uvc
import cv2

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Server has started")
    devices = uvc.device_list()
    print(devices)
    cap = uvc.Capture(devices[0]["uid"])
    cap.frame_size = (1920, 1080)
    app.state.cap = cap


@app.get("/")
def home():
    return {"message": "Hello, World!"}

@app.get("/photo")
def photo():
    frame = app.state.cap.get_frame_robust()
    img = cv2.imencode('.jpg', frame.img)[1].tobytes()
    return Response(img, media_type="image/jpg")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
