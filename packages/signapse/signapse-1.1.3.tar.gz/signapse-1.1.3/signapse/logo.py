import numpy as np
import cv2
# import matplotlib.pyplot as plt

class LOGO():
    def __init__(self, logo_path):
        super(LOGO,self).__init__()
        self.logo_path=logo_path   
        
   
    def get_centre(self,heatmap,logo_distance= 140): 
        x_ = int(np.nonzero(heatmap.sum(axis=0))[-1]) # -1 refer to the last pixel, which is to the right
        #y_ = (int(np.nonzero(heatmap[:,x_])[0].item())-(786))/heatmap.shape[0] #int(np.mean(np.array(np.nonzero(heatmap.sum(axis=1)))))
        x_ = (x_- 846)/7  # 7 to stabilize the logo centre
        
        #logo_centre = [y - (logo_distance+120) , x - logo_distance]
        # logo_centre = [int(496+y_), int(676+x_)]
        logo_centre = [int(496), int(676+x_)]
        
        # Maxmizing the arm width
        kernel_size = 45  # Adjust this size to increase the line width
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        dilated_image = cv2.dilate(np.array(heatmap), kernel, iterations=1)
        return logo_centre, dilated_image
    
    def get_logo(self,centre,image,size = (96,32)):
        logo = cv2.imread(self.logo_path, cv2.IMREAD_UNCHANGED)[100:920,100:810] #[:,:1024]  # [:,:1024] just the logo without text
        resized_logo = cv2.resize(logo,size)
        mask = resized_logo[:,:,-1]
        
        img = image[centre[0]-(size[1]//2):centre[0]+(size[1]//2),centre[1]-(size[0]//2):centre[1]+(size[0]//2),:]
        #img[img>40] = 22
        bgr_values = [int(x) for x in np.median(img, axis=(0, 1))]   #img.mean(axis=0).mean(axis=0)  #np.median(img, axis=(0, 1))  #np.min(img, axis=(0, 1))
        bgr_image = np.full_like(resized_logo[:, :, :3], bgr_values, dtype=np.uint8)
        
        logo_intra_detail =  cv2.bitwise_and((resized_logo[:,:,:3].astype('float')/2).astype('uint8'), cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))        
        logo_background_detail =  cv2.bitwise_and(bgr_image, cv2.cvtColor((255-mask), cv2.COLOR_GRAY2BGR))
        
        logo_2 = (logo_intra_detail + logo_background_detail)        
        return cv2.cvtColor(logo_2, cv2.COLOR_RGB2BGR)
    
    def get_mask(self,crops):
        background_value = np.median(crops, axis=(0, 1))
        crops[crops==background_value] = 0
        crops[crops!=0] = 1
        crops = cv2.dilate(np.array(crops), np.ones((5,5), np.uint8), iterations=2)
        return crops
    
    def add_masks(self,mask_crops,mask_arm):
        mask = mask_crops+mask_arm
        mask[mask>1] = 1
        return 255 * mask
    
    def stick_logo(self,image,logo,logo_centre,mask):
        height, width, _ = logo.shape
        a,b,c,d = (logo_centre[0]-(height//2)),(logo_centre[0]+(height//2)),(logo_centre[1]-(width//2)),(logo_centre[1]+(width//2))
        new_mask = cv2.cvtColor(mask[a:b,c:d], cv2.COLOR_GRAY2BGR).astype(np.uint8)
        updated_logo =  cv2.bitwise_and(logo,255 -new_mask)
        sub_image = cv2.bitwise_and(image[a:b,c:d],new_mask)
        final_logo = updated_logo + sub_image        
        image[a:b,c:d] = final_logo
        return image
    
    def add_logo(self,image,heatmap,crops):        
        logo_centre, mask_arm = self.get_centre(heatmap, logo_distance= 170)
        logo = self.get_logo(logo_centre,image,size = (64,64)) 
        mask_crops = self.get_mask(crops)
        mask = self.add_masks(mask_crops,mask_arm)
        image_with_logo = self.stick_logo(image,logo,logo_centre,mask)
        return image_with_logo
