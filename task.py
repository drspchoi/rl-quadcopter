import numpy as np
from physics_sim import PhysicsSim

class Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        distance1=np.sqrt(((self.sim.pose[:3]-self.target_pos)**2).sum())
        distance=np.tanh(distance1/10)
        distance2=distance1/10
        reward = np.tanh(1.-.0003*(abs(self.sim.pose[:3] - self.target_pos)).sum())-0.04*distance
        Xdistance=np.sqrt((self.sim.pose[:3][0]-self.target_pos[0])**2)
        Xdistance=np.tanh(Xdistance/10)
        Ydistance=np.sqrt((self.sim.pose[:3][1]-self.target_pos[1])**2)
        Ydistance=np.tanh(Ydistance/10)
        Zdistance1=np.sqrt((self.sim.pose[:3][2]-self.target_pos[2])**2)
        Zdistance=np.tanh(Zdistance1/10)
        Difference=Xdistance+Ydistance+1.5*Zdistance
        
        if Zdistance>0.999:
            reward=reward-0.35
        else:
            reward=reward+0.5

        if distance2<5.93:
            reward=reward+0.5
        else:
            reward=reward-0.35
           
        if Difference>1.6 or Difference<1.2: 
            reward=reward+0.3
      

            


        return reward

    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)
        next_state = np.concatenate(pose_all)
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state