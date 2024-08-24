import os
import cv2
import imageio
import shutil
import torch
import numpy as np
import subprocess
from pathlib import Path
from sam2.build_sam import build_sam2_video_predictor
import mediapipe as mp
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
from scipy.signal import find_peaks
# from signapse.heatmaps import HEATMAPS

import numpy as np
from scipy.signal import find_peaks

def find_top_image_differences(images, num_peaks=5, peak_height_threshold=6000):
    """
    Identify the top N differences between consecutive images based on the peak of absolute differences.

    Parameters:
    images (list of np.array): List of images in NumPy array format.
    num_peaks (int): Number of top peaks to find. Defaults to 5.
    peak_height_threshold (int or float): Minimum height of peaks to consider. Defaults to 6000.

    Returns:
    list: Indices of the top N peaks sorted in ascending order.
    """
    # Validate inputs
    if not images or len(images) < 2:
        raise ValueError("The input 'images' should be a list containing at least two images.")
    if num_peaks <= 0:
        raise ValueError("The number of peaks 'num_peaks' should be greater than zero.")
    
    # Compute absolute differences between consecutive images
    subtracted_images = [
        abs(np.sum(images[i].squeeze()) - np.sum(images[i - 1].squeeze()))
        for i in range(1, len(images))
    ]
    result = np.array(subtracted_images)
    # Find peaks above the specified height
    peaks, _ = find_peaks(result, height=peak_height_threshold)    
    if len(peaks) == 0:
        return []  # No peaks found    
    # Sort peaks by their prominence (absolute difference value) in descending order
    sorted_indices = np.argsort(result[peaks])[::-1]
    top_peaks = peaks[sorted_indices[:num_peaks]]    
    # Return indices of the top peaks, sorted in ascending order for clarity
    return sorted(top_peaks + 1)  # Correct indexing for returned peak positions

def get_wrist_points(frame):
    height, width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)    
    if results.pose_landmarks:
        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]        
        left_wrist_coords = [int(left_wrist.x * width), int(left_wrist.y * height)]
        right_wrist_coords = [int(right_wrist.x * width), int(right_wrist.y * height)]
        face_center_coords = [int(nose.x * width), int(nose.y * height)]        
        return [left_wrist_coords, right_wrist_coords, face_center_coords]
    else:
        return None, None, None
    
def save_masks( no_frame_names, video_segments, vis_frame_stride=1):
    mask=[]
    for out_frame_idx in range(0, no_frame_names, vis_frame_stride):        
        for _, out_mask in video_segments[out_frame_idx].items():
            mask.append(out_mask)

    return mask

class SAM2Initializer:
    def __init__(self, checkpoint_path, model_config_path):
        self.checkpoint_path = checkpoint_path
        self.model_config_path = model_config_path

        # Ensure we're using bfloat16 precision for the entire notebook
        self.autocast = torch.autocast(device_type="cuda", dtype=torch.bfloat16)
        self.autocast.__enter__()

        # Check for GPU compatibility
        if torch.cuda.is_available() and torch.cuda.get_device_properties(0).major >= 8:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True

        # Build the SAM 2 predictor
        self.predictor = self._initialize_predictor()

    def _initialize_predictor(self):
        """Initialize the SAM 2 video predictor."""
        return build_sam2_video_predictor(self.model_config_path, self.checkpoint_path)

    def get_predictor(self):
        """Return the initialized predictor."""
        return self.predictor

    def extract_frames(self, video_path, image_dir, ending_frame = None):
        reader = imageio.get_reader(video_path)
        fps = reader.get_meta_data().get('fps', None)
        reader.close()
        if fps is not None:
            if fps == 0:
                raise ValueError("FPS is 0, which is invalid")
        else:
            raise ValueError("FPS not found in video metadata")
        
        if Path(image_dir).exists() and Path(image_dir).is_dir():
            shutil.rmtree(Path(image_dir))
    
        Path(image_dir).mkdir(parents=True, exist_ok=True)
        output_pattern = Path(image_dir) / '%05d.jpg'

        ffmpeg_command = [
            'ffmpeg',
            '-i', video_path,
            '-q:v', '2',
            '-start_number', '0',
            '-pix_fmt', 'yuvj420p'
            # str(output_pattern)
        ]
        if ending_frame > 0:
            ffmpeg_command.extend(['-frames:v', str(ending_frame)])
        ffmpeg_command.extend([str(output_pattern)])

        try:
            subprocess.run(ffmpeg_command, check=True)
            print(f"Frames extracted and saved to: {image_dir}")
            return fps
        except subprocess.CalledProcessError as e:
            shutil.rmtree(image_dir)  # Clean up if error occurs
            raise ValueError(f"An error occurred while extracting frames: {e}")
        
    def add_points(self,points, labels, ann_frame_idx, ann_obj_id, predictor, inference_state):
        points = np.array(points, dtype=np.float32)
        labels = np.array(labels, np.int32)

        _, _, _ = predictor.add_new_points(  #.add_new_points_or_box(   this function has been added after the release in one week
            inference_state=inference_state,
            frame_idx=ann_frame_idx,
            obj_id=ann_obj_id,
            points=points,
            labels=labels,
        )
        return predictor
    
    def add_point_to_the_predictor(self,NUM_Frame, sam2_initializer, inference_state, tmp_image_dir, predictor):
        first_frame = cv2.imread(os.path.join(tmp_image_dir,f'{NUM_Frame:05d}.jpg'))
        points = get_wrist_points(first_frame)
        labels = [1,1,0] 
        ann_obj_id = 1
        predictor = sam2_initializer.add_points(points,labels, NUM_Frame, ann_obj_id, predictor, inference_state)
        return predictor
    
    def predict(self,predictor, inference_state):
        video_segments = {}
        for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(inference_state):
            video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }
        return video_segments
    
    


def get_masks_sam2(input_video, num_correction ,stop, tmp_dir = "./inputs/tmp"):
    model_cfg ="sam2_hiera_l.yaml"
    sam2_checkpoint ="./inputs/sam2_hiera_large.pt"    
    base_name = os.path.basename(input_video)
    filename, _ = os.path.splitext(base_name)
    tmp_image_dir = os.path.join(tmp_dir, filename)
    print(f'Get images from video.')
    sam2_initializer = SAM2Initializer(sam2_checkpoint, model_cfg)
    predictor = sam2_initializer.get_predictor()
    sam2_initializer.extract_frames(input_video, tmp_image_dir , ending_frame = stop)
    frame_names = [p for p in os.listdir(tmp_image_dir) if os.path.splitext(p)[-1] in [".jpg", ".jpeg", ".JPG", ".JPEG"]]
    frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))
    inference_state = predictor.init_state(video_path=tmp_image_dir)
    predictor.reset_state(inference_state)

    print(f'Feeding the points and propagating.')
    if num_correction > 0 :
        inc = int(len(frame_names)/num_correction)
        for NUM_Frame in range(inc,len(frame_names),inc):
            predictor = sam2_initializer.add_point_to_the_predictor(NUM_Frame, sam2_initializer, inference_state, tmp_image_dir, predictor)

    top_image_differences = [0] # initialise
    NUM_Frame = -1  # initialise
    counter = 0
    print(f'Correction based on the generated masks.')
    while len(top_image_differences) > 0  and counter < 3 :  # No more than a certain times for corrections.
        if NUM_Frame >= top_image_differences[0]: ## break if earlier frame failed 
            print(f'Stop correction because previous frame {top_image_differences[0]} failed.')
            break
        NUM_Frame = top_image_differences[0] 
        print(f'Correction attempt No {counter}. Frame no: {NUM_Frame}')
        predictor = sam2_initializer.add_point_to_the_predictor(NUM_Frame, sam2_initializer, inference_state, tmp_image_dir, predictor)
        video_segments = sam2_initializer.predict(predictor, inference_state)
        masks = save_masks(len(frame_names), video_segments)        
        top_image_differences = find_top_image_differences(masks)
        counter += 1

    shutil.rmtree(tmp_image_dir)
    return masks

        # if skin is needed, use the code below
        # for m in masks:
        #     f = cv2.imread(os.path.join(tmp_image_dir,f'{ann_frame_idx:05d}.jpg'))
        #     skin =  HEATMAPS().skin_detection(cv2.cvtColor(f, cv2.COLOR_BGR2RGB),'Rachel',include_hair = True) /255
        #     skin[skin>0]=1
