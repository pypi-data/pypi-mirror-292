import numpy as np
from sqlite3 import connect
from os import listdir
from random import randrange, choice
from pickle import dumps, loads, load
from copy import deepcopy
from gzip import open
from inspect import getouterframes, currentframe
from json import dump
import cv2, math
from matplotlib import pyplot as plt

class IrisSystem():
    def __init__(self, db_name: str, db_path: str = None) -> None:
        """Iris Database Control System 

        Args:
            db_name (str): Create new db
            db_path (str, optional): Add existing db. Defaults to None.
        """
        if not db_path:
            self.create_tables()
            self.db_name = db_name
        else: self.db_name = db_path
        self.recognizer = IrisRecognizer()

    def load_to_db(self, image_name: str, rois_id: int, img_path: str, show: bool = False):
        """Analyze iris and import data to db.

        Args:
            image_name (str): feature_tag
            rois_id (int) 
            img_path (str)
            show (bool, optional): Show while analyzing. Defaults to False.
        """
        rois = self.recognizer.load_rois_from_image(img_path, show)
        self.insert_iris(image_name, rois_id, rois)

    def create_tables(self):
        conn = connect(f'{self.db_name}.db')
        c = conn.cursor()

        # Create iris table
        c.execute('''
        CREATE TABLE IF NOT EXISTS iris (
            feature_tag TEXT PRIMARY KEY,
            iris_id INTEGER,
            kp_len INT,
            kp_filtered_len INT,
            desc_len INT,
            kp_desc_len INT
        )
        ''') # add feature numbers found here

        # Create feature tables
        feature_tables = ['right_side', 'left_side', 'bottom', 'complete']
        for table_name in feature_tables:
            c.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                feature_tag TEXT PRIMARY KEY,
                iris_id INTEGER,
                img BLOB,
                kp BLOB,
                pupil_circle BLOB,
                ext_circle BLOB,            
                des BLOB,
                FOREIGN KEY (iris_id) REFERENCES iris (iris_id)
            )
            ''')
        
        for table_name in feature_tables:
            c.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name}_img (
                feature_tag TEXT PRIMARY KEY,
                iris_id INTEGER,
                img_kp_init BLOB,
                img_kp_filtered BLOB,
                FOREIGN KEY (iris_id) REFERENCES iris (iris_id)
            )
            ''')

        conn.commit()
        conn.close()

    def insert_iris(self, feature_tag: str, iris_id: int, feature_data: dict, save_img: bool = False) -> bool:
        """Inserts iris data to database.

        Args:
            feature_tag (string)
            iris_id (int)
            feature_data (dict)
            save_img (bool, optional): Defaults to False.
        Returns:
            bool: True when no exception found.            
        """
        try:
            conn = connect(f'{self.db_name}.db')
            c = conn.cursor()

            # Insert into iris table
            c.execute('''
            INSERT INTO iris (iris_id, feature_tag, kp_len, kp_filtered_len, desc_len, kp_desc_len) VALUES (?, ?, ?, ?, ?, ?)
            ''', (iris_id, feature_tag, int(feature_data['kp_len']), int(feature_data['kp_filtered_len']), int(feature_data['desc_len']), int(feature_data['kp_desc_len'])))

            # Insert into feature tables
            if save_img:
                feature_tables = ['right_side', 'left_side', 'bottom', 'complete']
                for table_name in feature_tables:
                    data = feature_data.get(table_name.replace('_', '-'), {})
                    table_name = f"{table_name}_img"
                    if data:
                        c.execute(f'''
                        INSERT INTO {table_name} (iris_id, feature_tag, img_kp_init, img_kp_filtered)
                        VALUES (?, ?, ?, ?)
                        ''', (
                            iris_id,
                            feature_tag,
                            dumps(data['img_kp_init']),
                            dumps(data['img_kp_filtered']),
                        ))
                    
            feature_tables = ['right_side', 'left_side', 'bottom', 'complete']
            for table_name in feature_tables:
                data = feature_data.get(table_name.replace('_', '-'), {})
                if data:
                    serialized_kp = dumps(self.serialize_keypoints(data['kp']))
                    serialized_pupil_circle = dumps(data['pupil_circle'])
                    serialized_ext_circle = dumps(data['ext_circle'])
                    c.execute(f'''
                    INSERT INTO {table_name} (iris_id, feature_tag, img, kp, pupil_circle, ext_circle, des)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        iris_id,
                        feature_tag,
                        dumps(data['img']),
                        serialized_kp,
                        serialized_pupil_circle,
                        serialized_ext_circle,                
                        dumps(data['des'])
                    ))

            conn.commit()
            conn.close()
            print(f'Iris {feature_tag} is inserted to {self.db_name}...')
            return True
        except: return False

    def retrieve_iris(self, feature_tag: str, get_img: bool=False) -> dict:
        """Retrieves the iris data with the desired image tag.

        Args:
            feature_tag (str)
            get_img (bool, optional): Defaults to False.

        Returns:
            dict: Iris data
        """
        conn = connect(f'{self.db_name}.db')
        c = conn.cursor()

        # Initialize dictionary to store iris data
        iris_data = {}

        # Retrieve metadata from iris table
        c.execute('SELECT * FROM iris WHERE feature_tag = ?', (feature_tag,))
        iris_metadata = c.fetchone()
        if iris_metadata:
            iris_data['iris_metadata'] = iris_metadata

            # Retrieve feature data from specified tables
            feature_tables = ['right_side', 'left_side', 'bottom', 'complete']
            for table_name in feature_tables:
                dict_table_name = table_name.replace('_', '-')
                iris_data[dict_table_name] = {}

                # Retrieve keypoints and descriptors
                c.execute(f'SELECT * FROM {table_name} WHERE feature_tag = ?', (feature_tag,))
                rows = c.fetchall()
                for row in rows:
                    # Deserialize the feature data
                    img = loads(row[2])
                    kp = loads(row[3])
                    pupil_circle = loads(row[4])
                    ext_circle = loads(row[5])                
                    des = loads(row[6])
                    iris_data[dict_table_name]['img'] = img
                    iris_data[dict_table_name]['kp'] = self.deserialize_keypoints(kp)
                    iris_data[dict_table_name]['des'] = des
                    iris_data[dict_table_name]['pupil_circle'] = pupil_circle
                    iris_data[dict_table_name]['ext_circle'] = ext_circle

                # Retrieve image and related data if requested
                if get_img:
                    c.execute(f'SELECT * FROM {table_name}_img WHERE feature_tag = ?', (feature_tag,))
                    img_rows = c.fetchall()
                    for img_row in img_rows:
                        img_kp_init = loads(img_row[3])
                        img_kp_filtered = loads(img_row[4])
                        iris_data[dict_table_name]['img_kp_init'] = img_kp_init
                        iris_data[dict_table_name]['img_kp_filtered'] = img_kp_filtered

            # Retrieve additional information from the iris table
            c.execute('SELECT * FROM iris WHERE feature_tag = ?', (feature_tag,))
            iris_additional_info = c.fetchall()
            if iris_additional_info:
                for row in iris_additional_info:
                    # Deserialize additional feature data
                    kp_len = int(row[2])
                    kp_filtered_len = int(row[3])
                    desc_len = int(row[4])
                    kp_desc_len = int(row[5])

                    iris_data['kp_len'] = kp_len
                    iris_data['kp_filtered_len'] = kp_filtered_len
                    iris_data['desc_len'] = desc_len
                    iris_data['kp_desc_len'] = kp_desc_len

        conn.close()
        return iris_data

    def serialize_keypoints(self, keypoints) -> list[tuple]:
        """Convert list of cv2.KeyPoint objects to a serializable format."""
        return [(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in keypoints]

    def deserialize_keypoints(self, serialized_keypoints) -> list[cv2.KeyPoint]:
        """Convert serialized keypoints back to list of cv2.KeyPoint objects."""
        return [cv2.KeyPoint(x, y, size, angle, response, octave, class_id)
                for (x, y, size, angle, response, octave, class_id) in serialized_keypoints]

    def print_rois(self, data) -> None:
        """Print rois data to see dictionary and value types.

        Args:
            data (dict): Rois data
        """
        print("Dict data:")
        for key, value in data.items():
            if type(value) == dict:
                print(f"  {key}")
                for s_key,s_value in value.items():
                    print(f"    {s_key} : {type(s_value) if type(s_value) != tuple else {type(item) for item in s_value}}")
            else: print(f"{key} : {type(value) if type(value) != tuple else {type(item) for item in value}}")

    def check_if_not_exists(self, feature_tag: str) -> bool:
        """Check if the iris with the feature_tag exist in db. 

        Args:
            feature_tag (str): _description_

        Returns:
            bool: True if not exist
        """
        conn = connect(f'{self.db_name}.db')
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM iris WHERE feature_tag = ?", (feature_tag,))
        return cursor.fetchone() is None

    def compare_retireved_images(self, image_tag_1: str, image_tag_2: str, dratio: float = 0.8, stdev_angle: int = 10, stdev_dist: float = 0.15, show = False) -> dict:
        """Compare two irises from db.

        Args:
            image_tag_1 (str)
            image_tag_2 (str)
            Parameters:
                dratio (float, optional): Defaults to 0.8.
                stdev_angle (int, optional): Defaults to 10.
                stdev_dist (float, optional): Defaults to 0.15.
                show (bool, optional): Defaults to False.

        Returns:
            dict: Matche counts for each side
        """
        print(f"Analysing {image_tag_1} {image_tag_2}...")
        if not rois_1 and image_tag_1: rois_1 = self.retrieve_iris(image_tag_1)
        if not rois_2 and image_tag_2: rois_2 = self.retrieve_iris(image_tag_2)
        return self.recognizer.getall_matches(rois_1=rois_1, rois_2=rois_2, dratio=dratio, stdev_angle=stdev_angle, stdev_dist=stdev_dist, show=show)

    def get_random_row_with_id(self, iris_id: int) -> str:
        """Get random iris tag with iris_id.

        Args:
            iris_id (int)

        Returns:
            str: Iris tag (feature_tag)
        """
        conn = connect(f'{self.db_name}.db')
        cursor = conn.cursor()

        # Query to select a random row where feature_tag is 'x'
        query = """
        SELECT * FROM complete
        WHERE iris_id = ?
        ORDER BY RANDOM()
        LIMIT 1;
        """

        # Execute the query
        cursor.execute(query, (iris_id,))

        # Fetch the result
        random_row = cursor.fetchone()

        # Close the connection
        conn.close()
        return random_row[0]

    def test_parameters(self, db_size: int, write_data: bool = True, test_size_diff: int = 10, test_size_same: int = 10, dratio_list: list = [0.9, 0.95, 0.8, 0.75, 0.7], stdev_angle_list: list = [10, 20, 5, 25], stdev_dist_list: list = [0.10, 0.15, 0.20, 0.30]) -> dict:
        """Tests paramteres over current db.

        Args:
            db_size (int): Uniqe ID count in db. (Assuming ids starts from 0 and increases one by one.)
            write_data (bool, optional): Writes founded data to json. Defaults to True.
            test_size_diff (int, optional): Number of random rows to analyze for false data. Defaults to 10.
            test_size_same (int, optional): Number of random rows to analyze for true data. Defaults to 10.
            Parameters:
                dratio_list (list, optional): Defaults to [0.9, 0.95, 0.8, 0.75, 0.7].
                stdev_angle_list (list, optional): Defaults to [10, 20, 5, 25].
                stdev_dist_list (list, optional): Defaults to [0.10, 0.15, 0.20, 0.30].

        Returns:
            dict
        """
        possible_parameters = []

        for dratio in dratio_list:
            for stdev_angle in stdev_angle_list:
                for stdev_dist in stdev_dist_list:
                    possible_parameters.append({'dratio': dratio, 'stdev_angle': stdev_angle, 'stdev_dist': stdev_dist})

        results_dif = {}
        results_same = {}
        
        param_dict = {}
        param_dict['false_match'] = {}
        param_dict['true_match'] = {}
        param_dict['parameters'] = {}

        for param_id, parameter in enumerate(possible_parameters):
            param_dict['parameters'][param_id] = parameter
            results_dif[param_id] = {}
            results_same[param_id] = {}
            param_dict['false_match'][param_id] = []
            param_dict['true_match'][param_id] = []        
            for test_id in range(test_size_diff):
                try:
                    new_test = {}
                    number_list = list(range(db_size))
                    first_class = choice(number_list)
                    number_list.remove(first_class)
                    second_class = choice(number_list)
                    rois_1 = self.get_random_row_with_id(first_class)
                    rois_2 = self.get_random_row_with_id(second_class)
                    matches = self.compare_retireved_images(image_tag_1=rois_1[0], image_tag_2=rois_2[0], **parameter)
                    new_test['tags'] = [rois_1[0], rois_2[0]]
                    new_test['classes'] = [first_class, second_class]
                    new_test['matches'] = matches
                    new_test['parameter'] = parameter
                    results_dif[param_id][test_id] = new_test
                    param_dict['false_match'][param_id].append(int(matches['complete']))
                except: pass

            for test_id in range(test_size_same):
                try:
                    new_test = {}
                    number_list = list(range(6))
                    first_class = choice(number_list)
                    rois_1 = self.get_random_row_with_id(first_class)
                    rois_2 = self.get_random_row_with_id(first_class)
                    while rois_1[0] == rois_2[0]:
                        rois_2 = self.get_random_row_with_id(first_class)
                    matches = self.compare_retireved_images(image_tag_1=rois_1[0], image_tag_2=rois_2[0], **parameter)
                    new_test['tags'] = [rois_1[0], rois_2[0]]
                    new_test['classes'] = [first_class, first_class]
                    new_test['matches'] = matches
                    new_test['parameter'] = parameter
                    results_same[param_id][test_id] = new_test
                    param_dict['true_match'][param_id].append(int(matches['complete']))
                except: pass

        param_dict['false_match']['details'] = results_dif
        param_dict['true_match']['details'] = results_same
        
        with open('output.json', 'w') as json_file:
            dump(param_dict, json_file, indent=4)

        return param_dict

    def load_from_thousand(self, path: str = r'IrisDB/casia-iris-thousand-500mb/CASIA-Iris-Thousand/'):
        """Load data taken from https://www.kaggle.com/datasets/sondosaabed/casia-iris-thousand to db

        Args:
            path (str): Data folder path.
        """
        for id in range(0,1000):
            id_text = str(id).strip()
            while len(id_text) < 3:
                id_text = f"0{id_text}"
            print(f'\nChecking {id_text}...\n')
            for image in listdir(path+f"{id_text}/R"):
                iris_path = path+f"{id_text}/R/{image}"
                image_name = image.replace('.jpg','')
                if self.check_if_not_exists(image_name):
                    self.load_to_db(image_name, id, iris_path)
                else: print(f'{image_name} found in db.')

class IrisRecognizer():
    def __init__(self) -> None:
        pass
    
    def load_rois_from_image(self, filepath: str, show = True):
        img = self.load_image(filepath, show) # show=True
        print(f"\nImage loaded -> {(filepath.split('/'))[-3:]}")

        print(f"Getting iris boundaries ...")
        pupil_circle, ext_iris_circle = self.get_iris_boundaries(img, show=show) # Getting iris boundaries includes outer and inner boundary.
        if not pupil_circle or not ext_iris_circle:
            print("Error finding iris boundaries!")
            return

        print("Equalizing histogram ...")
        roi = self.get_equalized_iris(img, ext_iris_circle, pupil_circle, show=show)

        print("Getting roi iris images ...")
        rois = self.get_rois(roi, pupil_circle, ext_iris_circle, show=show)

        print("Searching for keypoints ...")
        sift = cv2.SIFT_create()
        self.load_keypoints(sift, rois, show=show)
        self.load_descriptors(sift, rois)

        print(f"Rois completed for {(filepath.split('/'))[-1].replace('.jpg', '')}.")
        return rois

    def load_image(self, filepath, show=False):
        img = cv2.imread(filepath, 0)
        if show:
            cv2.imshow(filepath, img)
            if cv2.waitKey(10000): pass
            cv2.destroyAllWindows()
        return img

    def get_iris_boundaries(self, img, show=False):
        # Finding iris inner boundary
        pupil_circle = self.find_pupil(img)

        if not pupil_circle:
            print('ERROR: Pupil circle not found!')
            return None, None

        # Finding iris outer boundary
        radius_range = int(math.ceil(pupil_circle[2]*1.5))
        multiplier = 0.25
        center_range = int(math.ceil(pupil_circle[2]*multiplier))
        ext_iris_circle = self.find_ext_iris(
                            img, pupil_circle, center_range, radius_range)

        while(not ext_iris_circle and multiplier <= 0.7):
            multiplier += 0.05
            print('Searching exterior iris circle with multiplier ' + str(multiplier))

            center_range = int(math.ceil(pupil_circle[2]*multiplier))
            ext_iris_circle = self.find_ext_iris(img, pupil_circle,
                                            center_range, radius_range)
        if not ext_iris_circle:
            print('ERROR: Exterior iris circle not found!')
            return None, None

        if show:
            cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
            self.draw_circles(cimg, pupil_circle, ext_iris_circle,
                        center_range, radius_range)
            cv2.imshow('iris boundaries', cimg)
            if cv2.waitKey(10000): pass
            cv2.destroyAllWindows()

        return pupil_circle, ext_iris_circle

    def find_pupil(self, img):
        def get_edges(image):
            edges = cv2.Canny(image,20,100)
            kernel = np.ones((3,3),np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=2)
            ksize = 2 * randrange(5,11) + 1
            edges = cv2.GaussianBlur(edges,(ksize,ksize),0)
            return edges

        param1 = 200 # 200
        param2 = 120 # 150
        pupil_circles = []
        while(param2 > 35 and len(pupil_circles) < 100):
            for mdn,thrs in [(m,t) for m in [3,5,7] for t in [20,40,45,50]]: # 25,30,35,55,60
                # Median Blur
                median = cv2.medianBlur(img, 2*mdn+1)
                # cv2.imshow("median",median)
                # cv2.imshow("img",img)
                # Threshold
                ret, thres = cv2.threshold(median, thrs, 255,cv2.THRESH_BINARY_INV)
                # cv2.imshow("thres",thres)

                # Fill Contours
                contours, hierarchy = cv2.findContours(thres.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
                draw_con = cv2.drawContours(thres, contours, -1, (255), -1)
                # cv2.imshow("draw_con",draw_con)
                # Canny Edges
                edges = get_edges(thres)
                # cv2.imshow("edges",edges)
                # HoughCircles
                circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 1,np.array([]), param1, param2)
                if circles is not None and circles.size > 0:
                    # convert the (x, y) coordinates and radius of the circles to integers
                    circles = np.round(circles[0, :]).astype("int")
                    for c in circles:
                        pupil_circles.append(c)

            param2 = param2 -1

        cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

        return self.get_mean_circle(pupil_circles)

    def get_mean_circle(self, circles, draw=None):
        # print(len(circles), circles)
        # for item in circles:
        #     print(item.size)
        if not circles:
            return
        mean_0 = int(np.mean([c[0] for c in circles]))
        mean_1 = int(np.mean([c[1] for c in circles]))
        mean_2 = int(np.mean([c[2] for c in circles]))

        if draw is not None:
            draw = draw.copy()
            # draw the outer circle
            cv2.circle(draw,(mean_0,mean_1),mean_2,(0,255,0),1)
            # draw the center of the circle
            cv2.circle(draw,(mean_0,mean_1),2,(0,255,0),2)
            cv2.imshow('mean circle', draw)
            if cv2.waitKey(10000): pass
            cv2.destroyAllWindows()

        return mean_0, mean_1, mean_2

    def find_ext_iris(self, img, pupil_circle, center_range, radius_range):
        def get_edges(image, thrs2):
            thrs1 = 0 # 0
            edges = cv2.Canny(image, thrs1, thrs2, apertureSize=5)
            kernel = np.ones((3,3),np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            ksize = 2 * randrange(5,11) + 1
            edges = cv2.GaussianBlur(edges,(ksize,ksize),0)
            return edges

        def get_circles(hough_param, median_params, edge_params):
            crt_circles = []
            for mdn,thrs2 in [(m,t)
                            for m in median_params
                            for t in edge_params]:
                # Median Blur
                median = cv2.medianBlur(img, 2*mdn+1)

                # Canny Edges
                edges = get_edges(median, thrs2)

                # HoughCircles
                circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 1,
                                        np.array([]), 200, hough_param)
                if circles is not None and circles.size > 0:
                    # convert the (x, y) coordinates and radius of the
                    # circles to integers
                    circles = np.round(circles[0, :]).astype("int")
                    for (c_col, c_row, r) in circles:
                        if self.point_in_circle(
                                int(pupil_circle[0]), int(pupil_circle[1]),
                                center_range, c_col, c_row) and \
                        r > radius_range:
                            crt_circles.append((c_col, c_row, r))
            return crt_circles

        param2 = 120 # 150
        total_circles = []
        while(param2 > 40 and len(total_circles) < 50):
            crt_circles = get_circles(
                            param2, [8,10,12,14,16,18,20], [430,480,530])
            if crt_circles:
                total_circles += crt_circles
            param2 = param2 -1

        if not total_circles:
            print("Running plan B on finding ext iris circle")
            param2 = 120
            while(param2 > 40 and len(total_circles) < 50):
                crt_circles = get_circles(
                                param2, [3,5,7,21,23,25], [430,480,530])
                if crt_circles:
                    total_circles += crt_circles
                param2 = param2 -1

        if not total_circles:
            return

        cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
        if cv2.waitKey(10000): pass
        filtered = self.filtered_circles(total_circles)

        return self.get_mean_circle(filtered)

    def point_in_circle(self, c_col, c_row, c_radius, p_col, p_row):
        return self.distance(c_col, c_row, p_col, p_row) <= c_radius

    def filtered_circles(self, circles, draw=None):
        # what if there are only 2 circles - which is alpha?
        def get_alpha_radius(circles0):
            alpha_circle = None
            dist_min = None
            circles1 = circles0[:]
            circles2 = circles0[:]
            for crt_c in circles1:
                dist = 0
                for c in circles2:
                    dist += math.fabs(float(crt_c[2]) - float(c[2]))
                if not dist_min or dist < dist_min:
                    dist_min = dist
                    alpha_circle = crt_c
            return alpha_circle[2]

        if not circles:
            print('Error: empty circles list in filtered_circles() !')
            return []
        c_0_mean, c_0_dev = self.standard_dev([int(i[0]) for i in circles])
        c_1_mean, c_1_dev = self.standard_dev([int(i[1]) for i in circles])
        filtered = []
        filtered_pos = []
        not_filtered = []
        ratio = 1.5
        for c in circles[:]:
            if c[0] < c_0_mean - ratio*c_0_dev or \
            c[0] > c_0_mean + ratio*c_0_dev or \
            c[1] < c_1_mean - ratio*c_1_dev or \
            c[1] > c_1_mean + ratio*c_1_dev:
                not_filtered.append(c)
            else:
                filtered_pos.append(c)
        if len([float(c[2]) for c in filtered_pos]) < 3:
            filtered = filtered_pos
        else:
            alpha_radius = get_alpha_radius(filtered_pos)
            mean_radius, dev_radius = self.standard_dev(
                                        [float(c[2]) for c in filtered_pos])
            max_radius = alpha_radius + dev_radius
            min_radius = alpha_radius - dev_radius
            for c in filtered_pos:
                if c[2] < min_radius or \
                c[2] > max_radius:
                    not_filtered.append(c)
                else:
                    filtered.append(c)

        if draw is not None:
            draw = draw.copy()
            for circle in not_filtered:
                # draw the outer circle
                cv2.circle(draw,(circle[0],circle[1]),circle[2],(255,0,0),1)
                # draw the center of the circle
                cv2.circle(draw,(circle[0],circle[1]),2,(255,0,0),2)
            for circle in filtered:
                # draw the outer circle
                cv2.circle(draw,(circle[0],circle[1]),circle[2],(0,255,0),1)
                # draw the center of the circle
                cv2.circle(draw,(circle[0],circle[1]),2,(0,255,0),2)
            cv2.imshow('filtered_circles() total={0} filtered_pos={1} filtered={2}'.\
                    format(len(circles), len(filtered_pos), len(filtered)),
                    draw)
            if cv2.waitKey(10000): pass
            cv2.destroyAllWindows()
        return filtered

    def draw_circles(self, cimg, pupil_circle, ext_iris_circle,
                    center_range=None, radius_range=None):
        # draw the outer pupil circle
        cv2.circle(cimg,(pupil_circle[0], pupil_circle[1]), pupil_circle[2],
                        (0,0,255),1)
        # draw the center of the pupil circle
        cv2.circle(cimg,(pupil_circle[0],pupil_circle[1]),1,(0,0,255),1)
        if center_range:
            # draw ext iris center range limit
            cv2.circle(cimg,(pupil_circle[0], pupil_circle[1]), center_range,
                            (0,255,255),1)
        if radius_range:
            # draw ext iris radius range limit
            cv2.circle(cimg,(pupil_circle[0], pupil_circle[1]), radius_range,
                            (0,255,255),1)
        # draw the outer ext iris circle
        cv2.circle(cimg, (ext_iris_circle[0], ext_iris_circle[1]),
                ext_iris_circle[2],(0,255,0),1)
        # draw the center of the ext iris circle
        cv2.circle(cimg, (ext_iris_circle[0], ext_iris_circle[1]),
                1,(0,255,0),1)

    def get_equalized_iris(self, img, ext_iris_circle, pupil_circle, show=False):
        def find_roi():
            mask = img.copy()
            mask[:] = (0)

            cv2.circle(mask,
                    (ext_iris_circle[0], ext_iris_circle[1]),
                    ext_iris_circle[2], (255), -1)
            cv2.circle(mask,
                    (pupil_circle[0],pupil_circle[1]),
                    pupil_circle[2],(0), -1)

            # cv2.imshow('mask iris', mask) # mask for boundaries

            roi = cv2.bitwise_and(img, mask)

            return roi

        roi = find_roi()

        # cv2.imshow('roi', roi) # see roi

        # Mask the top side of the iris
        for p_col in range(roi.shape[1]):
            for p_row in range(roi.shape[0]):
                theta = self.angle_v(ext_iris_circle[0], ext_iris_circle[1],
                                p_col, p_row)
                if theta > 50 and theta < 130:
                    roi[p_row,p_col] = 0 # crop from mask between degrees 50 and 130 to avoid eyelashes

        ret, roi = cv2.threshold(roi,50,255,cv2.THRESH_TOZERO)

        # cv2.imshow('roi-top', roi) # see roi

        equ_roi = roi.copy()
        cv2.equalizeHist(roi, equ_roi) # Histogram equalization is a method in image processing of CONTRAST ADJUSMENT using the image’s histogram.
        # cv2.imshow('roi-equalizeHist', roi) # see roi
        roi = cv2.addWeighted(roi, 0.0, equ_roi, 1.0, 0) # Use the addWeighted() function to blend images.

        if show:
            cv2.imshow('equalized histogram iris region', roi) # cv2.imshow('roi-addWeighted', roi) # see roi
            if cv2.waitKey(10000): pass
            cv2.destroyAllWindows()

        return roi

    def get_rois(self, img, pupil_circle, ext_circle, show=False):
        bg = img.copy()
        bg[:] = 0

        init_dict = {'img': bg.copy(),
                    'pupil_circle': pupil_circle,
                    'ext_circle': ext_circle,
                    'kp': None,
                    'img_kp_init': bg.copy(),
                    'img_kp_filtered': bg.copy(),
                    'des': None
                    }

        rois = {'right-side': deepcopy(init_dict),
                'left-side': deepcopy(init_dict),
                'bottom': deepcopy(init_dict),
                'complete': deepcopy(init_dict)
                }


        # cv2.imshow("rois['right-side']['img'] Before", rois['right-side']['img'])
        for p_col in range(img.shape[1]):
            for p_row in range(img.shape[0]):
                if not self.point_in_circle(pupil_circle[0], pupil_circle[1],
                                    pupil_circle[2], p_col, p_row) and \
                self.point_in_circle(ext_circle[0], ext_circle[1], ext_circle[2],
                                    p_col, p_row): # check if the point is in the pupil mask
                    theta = self.angle_v(ext_circle[0], ext_circle[1], p_col, p_row)
                    if theta >= -50 and theta <= 50:
                        rois['right-side']['img'][p_row,p_col] = img[p_row,p_col]
                    if theta >= 130 or theta <= -130:
                        rois['left-side']['img'][p_row,p_col] = img[p_row,p_col]
                    if theta >= -140 and theta <= -40:
                        rois['bottom']['img'][p_row,p_col] = img[p_row,p_col]
                    rois['complete']['img'][p_row,p_col] = img[p_row,p_col] # checks if the point is in the desired angles and create images for sides
        # cv2.imshow("rois['right-side']['img'] After", rois['right-side']['img'])

        rois['right-side']['ext_circle'] = \
                (0, int(1.25*ext_circle[2]), int(ext_circle[2]))
        rois['left-side']['ext_circle'] = \
                (int(1.25*ext_circle[2]),
                int(1.25*ext_circle[2]),
                int(ext_circle[2]))
        rois['bottom']['ext_circle'] = \
                (int(1.25*ext_circle[2]), 0, int(ext_circle[2]))
        rois['complete']['ext_circle'] = \
                (int(1.25*ext_circle[2]),
                int(1.25*ext_circle[2]),
                int(ext_circle[2]))

        # cv2.imshow("rois['right-side']['img'] Before", rois['right-side']['img'])
        for pos in ['right-side','left-side','bottom','complete']:
            tx = rois[pos]['ext_circle'][0] - ext_circle[0]
            ty = rois[pos]['ext_circle'][1] - ext_circle[1]
            rois[pos]['pupil_circle'] = (int(tx + pupil_circle[0]),
                                        int(ty + pupil_circle[1]),
                                        int(pupil_circle[2])) # The pupil's position (pupil_circle) in the current ROI is updated by adding the calculated offsets tx and ty to its x and y coordinates. The radius of the pupil (pupil_circle[2]) remains unchanged.
            M = np.float32([[1,0,tx],[0,1,ty]])
            rois[pos]['img'] = cv2.warpAffine(
                                rois[pos]['img'], M,
                                (img.shape[1], img.shape[0]))
        # cv2.imshow("rois['right-side']['img'] After", rois['right-side']['img'])

        # print(type(rois['right-side']['img']), type(ext_circle))
        # print(rois['right-side']['img'].shape, ext_circle[2])

        # cv2.imshow("rois['right-side']['img'] Before", rois['right-side']['img'])

        rois['right-side']['img'] = rois['right-side']['img'][0:int(2.5*ext_circle[2]), 0:int(1.25*ext_circle[2])]
        rois['left-side']['img'] = rois['left-side']['img'][0:int(2.5*ext_circle[2]), 0:int(1.25*ext_circle[2])]
        rois['bottom']['img'] = rois['bottom']['img'][0:int(1.25*ext_circle[2]), 0:int(2.5*ext_circle[2])]
        rois['complete']['img'] = rois['complete']['img'][0:int(2.5*ext_circle[2]), 0:int(2.5*ext_circle[2])]

        # cv2.imshow("rois['right-side']['img'] After", rois['right-side']['img'])


        if show:
            plt.subplot(2,2,1),plt.imshow(rois['right-side']['img'], cmap='gray')
            plt.title('right-side'),plt.xticks([]),plt.yticks([])
            plt.subplot(2,2,2),plt.imshow(rois['left-side']['img'], cmap='gray')
            plt.title('left-side'),plt.xticks([]),plt.yticks([])
            plt.subplot(2,2,3),plt.imshow(rois['bottom']['img'], cmap='gray')
            plt.title('bottom'),plt.xticks([]),plt.yticks([])
            plt.subplot(2,2,4),plt.imshow(rois['complete']['img'], cmap='gray')
            plt.title('complete'),plt.xticks([]),plt.yticks([])
            print("Showing only sides grey images...")
            plt.show()

        return rois

    def load_keypoints(self, sift, rois, show=False):
        bf = cv2.BFMatcher()


        for pos in ['right-side','left-side','bottom','complete']:
            # cv2.imshow(f"rois['{pos}']['img_kp_init'] Before", rois[pos]['img_kp_init'])
            rois[pos]['kp'] = sift.detect(rois[pos]['img'],None)
            # for i, kp in enumerate(rois[pos]['kp'][0:2]):
            #     print(f"KeyPoint {i}:")
            #     print(f"  - Position (x, y): ({kp.pt[0]}, {kp.pt[1]})")
            #     print(f"  - Size: {kp.size}")
            #     print(f"  - Angle: {kp.angle}")
            #     print(f"  - Response: {kp.response}")
            #     print(f"  - Octave: {kp.octave}")
            #     print(f"  - Class ID: {kp.class_id}")
            # Create image with non-filtered keypoints
            rois[pos]['img_kp_init'] = cv2.drawKeypoints(
                                            rois[pos]['img'], rois[pos]['kp'],
                                            color=(0,255,0), flags=0,
                                            outImage=None)
            # cv2.imshow(f"rois['{pos}']['img_kp_init'] After", rois[pos]['img_kp_init'])
            cv2.circle(
                rois[pos]['img_kp_init'],
                (rois[pos]['pupil_circle'][0], rois[pos]['pupil_circle'][1]),
                rois[pos]['pupil_circle'][2], (0,0,255), 1)
            cv2.circle(
                rois[pos]['img_kp_init'],
                (rois[pos]['ext_circle'][0], rois[pos]['ext_circle'][1]),
                rois[pos]['ext_circle'][2], (0,255,255), 1)


            # Filter detected keypoints
            inside = 0
            outside = 0
            wrong_angle = 0
            if pos == 'complete' : rois['kp_len'] = len(rois[pos]['kp'])
            kp_list = list(rois[pos]['kp'][:])
            for kp in kp_list:
                c_angle = self.angle_v(rois[pos]['ext_circle'][0],
                                rois[pos]['ext_circle'][1],
                                kp.pt[0], kp.pt[1])
                if self.point_in_circle(rois[pos]['pupil_circle'][0],
                                rois[pos]['pupil_circle'][1],
                                rois[pos]['pupil_circle'][2]+3,
                                kp.pt[0], kp.pt[1]):
                    kp_list.remove(kp)
                    inside +=1
                elif not self.point_in_circle(rois[pos]['ext_circle'][0],
                                        rois[pos]['ext_circle'][1],
                                        rois[pos]['ext_circle'][2]-5,
                                        kp.pt[0], kp.pt[1]):
                    kp_list.remove(kp)
                    outside +=1
                elif (pos == 'right-side' and (c_angle <= -45 or c_angle >= 45)) or \
                    (pos == 'left-side' and (c_angle <= 135 and c_angle >= -135)) or \
                    (pos == 'bottom' and (c_angle <= -135 or c_angle >= -45)):
                    kp_list.remove(kp)
                    wrong_angle +=1
            rois[pos]['kp'] = tuple(kp_list)
            if pos == 'complete' : rois['kp_filtered_len'] = len(rois[pos]['kp'])

            # Create images with filtered keypoints
            rois[pos]['img_kp_filtered'] = cv2.drawKeypoints(
                                    rois[pos]['img'],rois[pos]['kp'],
                                    color=(0,255,0), flags=0,
                                    outImage=None)
            cv2.circle(
                rois[pos]['img_kp_filtered'],
                (rois[pos]['pupil_circle'][0],rois[pos]['pupil_circle'][1]),
                rois[pos]['pupil_circle'][2], (0,0,255), 1)
            cv2.circle(
                rois[pos]['img_kp_filtered'],
                (rois[pos]['ext_circle'][0],rois[pos]['ext_circle'][1]),
                rois[pos]['ext_circle'][2], (0,255,255), 1)

        # Show keypoints images
        if show:
            i=0
            for pos in ['right-side','left-side','bottom']:
                plt.subplot(3, 2, 2*i+1), \
                plt.imshow(rois[pos]['img_kp_init'])
                plt.xticks([]), plt.yticks([])
                plt.subplot(3, 2, 2*i+2), \
                plt.imshow(rois[pos]['img_kp_filtered'])
                plt.xticks([]), plt.yticks([])
                i+=1
            plt.show()

    def load_descriptors(self, sift, rois):
        for pos in ['right-side','left-side','bottom','complete']:
            rois[pos]['kp'], rois[pos]['des'] = \
                sift.compute( rois[pos]['img'], rois[pos]['kp'] )
        rois['desc_len'] = len(rois['complete']['des'])
        rois['kp_desc_len'] = len(rois['complete']['kp'])
            # cv2.imshow(f"rois[{pos}]['des']", rois[pos]['des'])
            # print(rois[pos]['des'][0:2])

    def getall_matches(self, rois_1, rois_2, dratio,
                    stdev_angle, stdev_dist, show=False):
        img_matches = []
        numberof_matches = {'right-side': 0,
                    'left-side': 0,
                    'bottom': 0,
                    'complete': 0}

        for pos in ['right-side','left-side','bottom','complete']:
            if not rois_1[pos]['kp'] or not rois_2[pos]['kp']:
                print("KeyPoints not found in one of rois_x[pos]['kp'] !!!")
                print(" -->", pos, len(rois_1[pos]['kp']), len(rois_2[pos]['kp']))
            else:
                matches = self.get_matches(rois_1[pos], rois_2[pos],
                                    dratio, stdev_angle, stdev_dist)
                numberof_matches[pos] = len(matches)

            if show:
                print("{0} matches: {1}".format(pos, str(len(matches))))
                crt_image = cv2.drawMatchesKnn(
                                rois_1[pos]['img'],rois_1[pos]['kp'],
                                rois_2[pos]['img'],rois_2[pos]['kp'],
                                [matches], flags=2, outImg=None)

                img_matches.append(crt_image)
                cv2.imshow('matches', crt_image)
                if cv2.waitKey(10000): pass
                cv2.destroyAllWindows()

        return numberof_matches

    def get_matches(self, roipos_1, roipos_2,
                    dratio, stdev_angle, stdev_dist):
        if not roipos_1['kp'] or not roipos_2['kp']:
            print("KeyPoints not found in one of roipos_x['kp'] !!!")
            return []

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(roipos_1['des'], roipos_2['des'], k=2)
        kp1 = roipos_1['kp']
        kp2 = roipos_2['kp']

        diff_dist_1 = roipos_1['ext_circle'][2] - roipos_1['pupil_circle'][2]
        diff_dist_2 = roipos_2['ext_circle'][2] - roipos_2['pupil_circle'][2]

        diff_angles = []
        diff_dists = []
        filtered = []
        for m,n in matches:
            if (m.distance/n.distance) > dratio:
                continue

            x1,y1 = kp1[m.queryIdx].pt
            x2,y2 = kp2[m.trainIdx].pt

            angle_1 = self.angle_v(
                    x1,y1,
                    roipos_1['pupil_circle'][0],
                    roipos_1['pupil_circle'][1])
            angle_2 = self.angle_v(
                    x2,y2,
                    roipos_2['pupil_circle'][0],
                    roipos_2['pupil_circle'][1])
            diff_angle = angle_1 - angle_2
            diff_angles.append(diff_angle)

            dist_1 = self.distance(x1,y1,
                            roipos_1['pupil_circle'][0],
                            roipos_1['pupil_circle'][1])
            dist_1 = dist_1 - roipos_1['pupil_circle'][2]
            dist_1 = dist_1 / diff_dist_1

            dist_2 = self.distance(x2,y2,
                            roipos_2['pupil_circle'][0],
                            roipos_2['pupil_circle'][1])
            dist_2 = dist_2 - roipos_2['pupil_circle'][2]
            dist_2 = dist_2 / diff_dist_2

            diff_dist = dist_1 - dist_2
            diff_dists.append(diff_dist)

            filtered.append(m)

        # Remove bad matches
        if True and filtered:
            median_diff_angle = self.median(diff_angles)
            median_diff_dist = self.median(diff_dists)
            #print("median dist:", median_diff_dist)
            for m in filtered[:]:
                x1,y1 = kp1[m.queryIdx].pt
                x2,y2 = kp2[m.trainIdx].pt

                angle_1 = self.angle_v(
                    x1,y1,
                    roipos_1['pupil_circle'][0],
                    roipos_1['pupil_circle'][1])
                angle_2 = self.angle_v(
                    x2,y2,
                    roipos_2['pupil_circle'][0],
                    roipos_2['pupil_circle'][1])
                diff_angle = angle_1 - angle_2

                good_diff_angle = \
                    (diff_angle > median_diff_angle - stdev_angle and \
                    diff_angle < median_diff_angle + stdev_angle)

                dist_1 = self.distance(x1,y1,
                                roipos_1['pupil_circle'][0],
                                roipos_1['pupil_circle'][1])
                dist_1 = dist_1 - roipos_1['pupil_circle'][2]
                dist_1 = dist_1 / diff_dist_1

                dist_2 = self.distance(x2,y2,
                                roipos_2['pupil_circle'][0],
                                roipos_2['pupil_circle'][1])
                dist_2 = dist_2 - roipos_2['pupil_circle'][2]
                dist_2 = dist_2 / diff_dist_2

                diff_dist = dist_1 - dist_2
                good_dist = (diff_dist > median_diff_dist - stdev_dist and \
                            diff_dist < median_diff_dist + stdev_dist)

                if good_diff_angle and good_dist:
                    continue

                filtered.remove(m)

        return filtered

    def angle_v(self, x1,y1,x2,y2):
        return math.degrees(math.atan2(-(y2-y1),(x2-x1))) # 'atan2' calculates the arctangent of the ratio of its two arguments, taking into account the signs of both to determine the correct quadrant of the angle.

    def distance(self, x1,y1,x2,y2):
        dst = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        return dst

    def mean(self, x):
        sum = 0.0
        for i in range(len(x)):
            sum += x[i]
        return sum/len(x)

    def median(self, x):
        return np.median(np.array(x))

    def standard_dev(self, x):
        if not x:
            print('Error: empty list parameter in standard_dev() !')
            print(getouterframes( currentframe() )[1])
            print()
            return None, None
        m = self.mean(x)
        sumsq = 0.0
        for i in range(len(x)):
            sumsq += (x[i] - m) ** 2
        return m, math.sqrt(sumsq/len(x))

    def load_rois_from_bin(self, bin_path):
        with open(bin_path, 'rb') as bin_file:
            rois = load(bin_file)
        self.unpickle_rois(rois)
        return rois

    def unpickle_rois(self, rois):
        for pos in ['right-side','left-side','bottom','complete']:
            rois[pos]['kp'] = self.unpickle_keypoints(rois[pos]['kp'])

    def unpickle_keypoints(self, array):
        keypoints = []
        for point in array:
            temp_kp = cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1],
                                _angle=point[2], _response=point[3],
                                _octave=point[4], _class_id=point[5])
            keypoints.append(temp_kp)
        return keypoints

    def pickle_rois(self, rois):
        for pos in ['right-side','left-side','bottom','complete']:
            rois[pos]['kp'] = self.pickle_keypoints(rois[pos]['kp'])

    def pickle_keypoints(self, keypoints):
        unfolded = []
        for point in keypoints:
            temp = (point.pt, point.size, point.angle, point.response,
                    point.octave, point.class_id)
            unfolded.append(temp)

        return unfolded

