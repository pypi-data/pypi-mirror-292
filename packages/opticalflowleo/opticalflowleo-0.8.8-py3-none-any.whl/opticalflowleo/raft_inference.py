import os
import torch
from .windflow_light.windflow import inference_flows

module_path = os.path.abspath(__file__)
package_dir = os.path.dirname(module_path)
model_file_path = package_dir + '/windflow_light/model_weights/windflow.raft.pth.tar'


class RAFT_inference:
    def __init__(self, tile_size=512,
                 overlap=128,
                 batch_size=1,
                 checkpoint_file=model_file_path):

        self.inference = inference_flows.FlowRunner('RAFT',
                                                    overlap=overlap,
                                                    tile_size=tile_size,
                                                    device=torch.device('cpu'),
                                                    batch_size=batch_size)
        self.inference.load_checkpoint(checkpoint_file)

    def do_inference(self, fld_t0, fld_t1, lon_1d, lat_1d, sec_per_step, convert_cartesian=True):
        _, flows = self.inference.forward(fld_t0, fld_t1)

        v, u = flows[1], flows[0]
        if convert_cartesian:
            v, u = inference_flows.cartesian_to_speed(lat_1d, lon_1d, v, u, sec_per_step=sec_per_step)

        return v, u
