import logging, torch, imageio, cv2, copy, os
import numpy as np
from pathlib import Path
from signapse.heatmaps import HEATMAPS
import signapse.constants as C


class GENERATOR():
    def __init__(self, args):
        super(GENERATOR,self).__init__()
        self.args=args 

    
    def mkdir_safe(self,path):
        Path(path).mkdir(parents=True, exist_ok=True)
        
    def set_new_shoulder_points(self,video_name,signer,remove_hip_pose,pose_tensor, tolerance=0):
        if signer == 'Jay':
            logging.info('SETTING JAY SHOULDER TO SPECIFIC VALUE')
            pose_tensor[:,0,:] = torch.from_numpy(np.array([0.70364093, 0.44848727])).to(pose_tensor.device)
            pose_tensor[:,1,:] = torch.from_numpy(np.array([0.29054845, 0.46131581])).to(pose_tensor.device)
            if not remove_hip_pose:
                pose_tensor[:,-2,:] = torch.from_numpy(np.array([0.63351321, 1])).to(pose_tensor.device)
                pose_tensor[:,-1,:] = torch.from_numpy(np.array([0.37140189, 1])).to(pose_tensor.device)
        elif signer == 'Marcel':
            tolerance=(20/1024)
            logging.info('SETTING JAY SHOULDER TO SPECIFIC VALUE')
            pose_tensor[:,0,:] = torch.from_numpy(np.array([0.72490184+tolerance, 0.41866337+tolerance])).to(pose_tensor.device)
            pose_tensor[:,1,:] = torch.from_numpy(np.array([0.2982856-tolerance,  0.41772193+tolerance])).to(pose_tensor.device)
            if not remove_hip_pose:
                pose_tensor[:,-2,:] = torch.from_numpy(np.array([0.63403587, 1])).to(pose_tensor.device)
                pose_tensor[:,-1,:] = torch.from_numpy(np.array([0.36255618, 1])).to(pose_tensor.device)
        elif signer == 'Rachel':
            logging.info('SETTING Rachel SHOULDER TO SPECIFIC VALUE')
            pose_tensor[:,0,:] = torch.from_numpy(np.array([0.70082947+tolerance, 0.48699772+tolerance])).to(pose_tensor.device)
            pose_tensor[:,1,:] = torch.from_numpy(np.array([0.33488731-tolerance, 0.49859208+tolerance])).to(pose_tensor.device)
            if not remove_hip_pose:
                pose_tensor[:,-2,:] = torch.from_numpy(np.array([0.63827938, 1])).to(pose_tensor.device)
                pose_tensor[:,-1,:] = torch.from_numpy(np.array([0.40874049, 1])).to(pose_tensor.device)  

            if video_name in C.HANDS_OFF_GLOSSES:           
                # Left Elbow
                pose_tensor[:, 2, :] = torch.from_numpy(np.array([0.76420859375, 0.79385185546875])).to(pose_tensor.device)
                # Left Wrist
                pose_tensor[:, 6, :] = torch.from_numpy(np.array([0.58, 0.81])).to(pose_tensor.device)
     
                
        return pose_tensor
    
    def import_crops(self,hand_crop,face_crop,sign_request_id, length):
        if hand_crop:
            hand_mask = np.load(f'./inputs/SAM_files/{sign_request_id}.npy')
        else:
            hand_mask = range(0,length)
            
        if face_crop:
            face_mask = np.load(f'./inputs/Face_files/{sign_request_id}.npy')
        else:
            face_mask = range(0,length)        
        return hand_mask, face_mask
    
    def apply_norm(self,cropped_frame,img_centre,min_size):
        cropped_frame = cropped_frame[img_centre[1]:img_centre[1]+img_centre[3], img_centre[0]:img_centre[0]+img_centre[2]]
        return cv2.resize(cropped_frame, (min_size, min_size))
    
    def get_face_mask(self,total_frames,img_centre,min_size,GAN_model,args):
        hand_mask, face_mask = self.import_crops(args.opt.hand_crop,args.opt.face_crop,args.sign_request_id, total_frames)
        reader = imageio.get_reader(args.input_video_path)
        crops = []
        counter = 0
        for input_frame in reader:
            if (counter < args.start):
                    continue
            if counter % 25 == 0:
                logging.info("Frame: {}".format(counter))
                
            if args.stop > 0 and counter >= args.stop:
                break
            # Crop the input image
            input_frame = self.apply_norm(input_frame,img_centre,min_size)
            MP_results = torch.zeros(178, 2).to(args.GPU)           
            _, hand_crops = HEATMAPS().get_heatmaps_crops(input_frame=input_frame,
                                                                MP_results_gen= MP_results,
                                                                GAN_model= GAN_model,  
                                                                args=args,
                                                                iii=counter,
                                                                hand_mask= hand_mask[counter],
                                                                face_mask= face_mask[counter]
                                                                )
            crops.append(hand_crops[:,160:430,400:630])    
            counter +=  1        
        crops = np.stack(crops, axis=0) 
        np.save(args.saving_file_path,crops)


        
    def create_pose_video_from_MP(self,img_centre,min_size,FPS,pose_tensor,GAN_model, only_pose=False):
        pose_tensor = self.set_new_shoulder_points(self.args.sign_request_id,self.args.signer,self.args.opt.remove_hip_pose,pose_tensor)      
        hand_mask, face_mask = self.import_crops(self.args.opt.hand_crop,self.args.opt.face_crop,self.args.sign_request_id, len(pose_tensor))
        
        # Create the output folder
        self.mkdir_safe(self.args.output_video_path)
        output_video_file = self.args.output_video_path + self.args.sign_request_id + ".mp4"
        output_video = imageio.get_writer(output_video_file, fps=float(FPS), codec='libx264',ffmpeg_params=['-crf', '10'], quality =10)   # crf = 23 default , lower value--> high equality, big size file
        logging.info(f"Producing Video at {output_video_file}")
        logging.info(f"\n")
        logging.info(f"Generating Pose video --- ")
        input_video_path = self.args.input_video_path
        if only_pose:
            reader = np.random.randint(5, size=(len(pose_tensor),1024, 1024, 3))
        else:
            reader = imageio.get_reader(input_video_path)
        crops,maps=[],[]
        counter = 0
        for input_frame in reader:
            if (counter < self.args.start):
                    continue
            if counter % 25 == 0:
                logging.info("Frame: {}".format(counter))
                
            if self.args.stop > 0 and counter >= self.args.stop:
                break
            # Crop the input image
            input_frame = self.apply_norm(input_frame,img_centre,min_size)
            # Extract the saved pose estimation result
            MP_results = copy.deepcopy(pose_tensor[counter])  
            
            heat_maps, hand_crops = HEATMAPS().get_heatmaps_crops(input_frame=input_frame,
                                                                MP_results_gen= MP_results,
                                                                GAN_model= GAN_model,  
                                                                args=self.args,
                                                                iii=counter,
                                                                hand_mask= hand_mask[counter],
                                                                face_mask= face_mask[counter]
                                                                )
            
            if self.args.opt.merge_crops:
                hand_crops = hand_crops.view((len(hand_crops)) // 2, 2, hand_crops.shape[1], hand_crops.shape[2]).sum(dim=1) + 1
                  
            if counter==0 and (self.args.opt.num_frames)>0:
                for _ in range(self.args.opt.num_frames):
                    maps.append(heat_maps)
                    crops.append(hand_crops)
                    
            maps.append(heat_maps)
            crops.append(hand_crops) 
            
            if (self.args.opt.num_frames)>counter:
                mid_input_frame = copy.deepcopy(input_frame)
                counter+=1
                continue
            
            if not self.args.opt.multi_frames:
                mid_input_frame = input_frame
                
        
            frame = HEATMAPS().generate_GAN_frame_maps_crops(mid_input_frame,
                                                             maps,
                                                             crops,
                                                             GAN_model= GAN_model,
                                                             opt=self.args.opt,
                                                             detailed_video=self.args.detailed_video
                                                             )
                
            

            # Write each generated frame to the output video
            output_video.append_data(frame)
            maps = maps[1:]
            crops =crops[1:]
            mid_input_frame = copy.deepcopy(input_frame)
            counter+=1
        
        if self.args.opt.multi_frames:
            # duplicate last frames as well 
            for _ in range(self.args.opt.num_frames):
                maps.append(heat_maps)
                crops.append(hand_crops)
                    
                frame = HEATMAPS().generate_GAN_frame_maps_crops(input_frame,
                                                            maps,
                                                            crops,
                                                            GAN_model= GAN_model,
                                                            opt=self.args.opt,
                                                            detailed_video=self.args.detailed_video                                                                                                
                                                            )
                output_video.append_data(frame)
                maps = maps[1:]
                crops =crops[1:]        
        
        if self.args.opt.hand_crop:
            os.remove(f'./inputs/SAM_files/{self.args.sign_request_id}.npy')
        if self.args.opt.face_crop:
            os.remove(f'./inputs/Face_files/{self.args.sign_request_id}.npy')
        output_video.close()
        if not only_pose:
            reader.close()
