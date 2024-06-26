import numpy as np
import matplotlib.pyplot as plt
from read_data import read_world, read_sensor_data
from matplotlib.patches import Ellipse
#from icecream import ic

# plot preferences, interactive plotting mode
fig = plt.figure()
plt.axis([-1, 12, 0, 10])
plt.ion()
plt.show()


def plot_state(mu, sigma, landmarks, map_limits):
    # Visualizes the state of the kalman filter.
    #
    # Displays the mean and standard deviation of the belief,
    # the state covariance sigma and the position of the 
    # landmarks.

    # landmark positions
    lx = []
    ly = []

    for i in range(len(landmarks)):
        lx.append(landmarks[i + 1][0])
        ly.append(landmarks[i + 1][1])

    # mean of belief as current estimate
    estimated_pose = mu

    # calculate and plot covariance ellipse
    covariance = sigma[0:2, 0:2]
    eigenvals, eigenvecs = np.linalg.eig(covariance)

    # get largest eigenvalue and eigenvector
    max_ind = np.argmax(eigenvals)
    max_eigvec = eigenvecs[:, max_ind]
    max_eigval = eigenvals[max_ind]

    # get smallest eigenvalue and eigenvector
    min_ind = 0
    if max_ind == 0:
        min_ind = 1

    min_eigval = eigenvals[min_ind]

    # chi-square value for sigma confidence interval
    chi_square_scale = 2.2789

    # calculate width and height of confidence ellipse
    width = 2 * np.sqrt(chi_square_scale * max_eigval)
    height = 2 * np.sqrt(chi_square_scale * min_eigval)
    angle = np.arctan2(max_eigvec[1], max_eigvec[0])

    # generate covariance ellipse
    ell = Ellipse(xy=[estimated_pose[0], estimated_pose[1]], width=width, height=height, angle=angle / np.pi * 180)
    ell.set_alpha(0.25)

    # plot filter state and covariance
    plt.clf()
    plt.gca().add_artist(ell)
    plt.plot(lx, ly, 'bo', markersize=10)
    plt.quiver(estimated_pose[0], estimated_pose[1], np.cos(estimated_pose[2]), np.sin(estimated_pose[2]), angles='xy',
               scale_units='xy')
    plt.axis(map_limits)

    plt.pause(0.01)


def prediction_step(odometry, mu, sigma):
    # Updates the belief, i.e., mu and sigma, according to the motion 
    # model
    # 
    # mu: 3x1 vector representing the mean (x,y,theta) of the 
    #     belief distribution
    # sigma: 3x3 covariance matrix of belief distribution 

    x = mu[0]
    y = mu[1]
    theta = mu[2]

    delta_rot1 = odometry['r1']
    delta_trans = odometry['t']
    delta_rot2 = odometry['r2']

    '''your code here'''

    x2 = x + delta_trans * np.cos(theta + delta_rot1)
    y2 = y + delta_trans * np.sin(theta + delta_rot1)
    th2 = theta + delta_rot1 + delta_rot2

    mu = [x2, y2, th2]

    G = np.array([
        [1, 0, -delta_trans * np.sin(theta + delta_rot1)],
        [0, 1, delta_trans * np.cos(theta + delta_rot1)],
        [0, 0, 1]
    ])

    V = np.array([
        [np.cos(theta + delta_rot1), -delta_trans * np.sin(theta + delta_rot1), 0],
        [np.sin(theta + delta_rot1), delta_trans * np.cos(theta + delta_rot1), 0],
        [0, 1, 1]
    ])

    Q = np.array(np.eye(3) * 0.2)

    sigma = G @ sigma @ G.T + V @ Q @ V.T

    '''***        ***'''

    return mu, sigma


def correction_step(sensor_data, mu, sigma, landmarks):
    # updates the belief, i.e., mu and sigma, according to the
    # sensor model
    # 
    # The employed sensor model is range-only
    #
    # mu: 3x1 vector representing the mean (x,y,theta) of the 
    #     belief distribution
    # sigma: 3x3 covariance matrix of belief distribution 

    x = mu[0]
    y = mu[1]
    theta = mu[2]

    # measured landmark ids and ranges
    ids = sensor_data['id']
    ranges = sensor_data['range']
    phiMass = sensor_data['bearing']

    z = np.array(ranges)

    R = np.eye(len(z)) * 0.5

    h = np.zeros(len(z))
    H = np.zeros([len(z), 3])


    for i in range(len(ids)):
        mx, my = landmarks[ids[i]]
        h[i] = np.sqrt(np.power(mx - x, 2) + np.power(my - y, 2))

        H[i] = [
            (x - mx) / (np.sqrt(np.power(mx - x, 2) + np.power(my - y, 2))),
            (y - my) / (np.sqrt(np.power(mx - x, 2) + np.power(my - y, 2))),
            0
        ]

    S = H @ sigma @ H.T + R
    K = sigma @ H.T @ np.linalg.inv(S)
    print(np.shape(mu))
    mu = mu + (K @ (z - h)).T
    print(np.shape(mu))
    I = np.eye(3)
    sigma = (I - K @ H) @ sigma
    return mu, sigma


def main():
    # implementation of an extended Kalman filter for robot pose estimation

    print("Reading landmark positions")
    landmarks = read_world("../data/world.dat")

    print("Reading sensor data")
    sensor_readings = read_sensor_data("../data/sensor_data.dat")

    # initialize belief
    mu = [0.0, 0.0, 0.0]
    sigma = np.array([[1.0, 0.0, 0.0],
                      [0.0, 1.0, 0.0],
                      [0.0, 0.0, 1.0]])

    map_limits = [-1, 12, -1, 10]

    # run kalman filter
    for timestep in range(len(sensor_readings) // 2):
        # plot the current state
        plot_state(mu, sigma, landmarks, map_limits)

        # perform prediction step
        mu, sigma = prediction_step(sensor_readings[timestep, 'odometry'], mu, sigma)

        # perform correction step
        mu, sigma = correction_step(sensor_readings[timestep, 'sensor'], mu, sigma, landmarks)

    plt.show(block=True)


if __name__ == "__main__":
    main()
