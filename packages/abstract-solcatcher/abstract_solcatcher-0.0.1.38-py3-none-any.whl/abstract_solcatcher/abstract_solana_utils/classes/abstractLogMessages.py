from abstract_utilities import make_list
from ..utils import *
class logMessageManager:
      def __init__(self,txnData):
        self.logMessages = get_log_messages(txnData)
        self.logClusters = self.get_log_index_clusters()
      def get_log_index_clusters(self):
        clusters =[]
        clusterCount=-1
        for j,log in enumerate(self.logMessages):
            curr_logs = {}
            
            # Split the log into parts based on whitespace
            parts = [part.replace(':','') for part in log.split()]
            
            if not parts:
                continue  # Skip empty lines
            # Parse based on the structure
            if "invoke" in parts:
                
                clusterCount+=1
                clusters.append({"logs":[],"clusterIndex":clusterCount,"programId":parts[1],"stackHeight":str(parts[-1])[1:-1],"start":j,"end":j,"types":[]})
                
                curr_logs['cmdType'] = parts[0]
                curr_logs['programId'] = parts[1]
                curr_logs['event'] = parts[2]  # 'invoke' or 'success'
                curr_logs['vars'] = parts[3] if len(parts) > 3 else None
            
            elif "consumed" in parts:
                curr_logs['cmdType'] = parts[0]
                curr_logs['programId'] = parts[1]
                curr_logs['event'] = 'consumed'
                consumed_index = parts.index('consumed')
                curr_logs['vars'] = " ".join(parts[consumed_index + 1:])
            
            elif "return:" in log:
                curr_logs['cmdType'] = parts[0]
                curr_logs['programId'] = parts[1]
                curr_logs['event'] = 'return'
                curr_logs['vars'] = " ".join(parts[2:])
            
            elif "log:" in log:
                curr_logs['cmdType'] = parts[0]
                curr_logs['programId'] = parts[1]
                log_index = parts.index('log')
                curr_logs['event'] = parts[log_index + 1]
                curr_logs['type'] = parts[log_index + 2] if len(parts) > log_index + 2 else None
                clusters[-1]['types'].append(curr_logs['type'])
                if clusters[-1].get('type') == None:
                  clusters[-1]['type']=curr_logs['type']
                curr_logs['vars'] = " ".join(parts[log_index + 3:]) if len(parts) > log_index + 3 else None
            
            else:
                curr_logs['cmdType'] = parts[0]
                curr_logs['programId'] = parts[1]
                curr_logs['event'] = parts[2] if len(parts) > 2 else None
                curr_logs['vars'] = " ".join(parts[3:]) if len(parts) > 3 else None
            clusters[-1]['end']=j
            # Store parsed log in the list
            clusters[-1]["logs"].append(curr_logs)
        return clusters      
      def get_cluster_type_from_index(self,index):
        cluster = {}
        if len(self.logClusters) >index:
          cluster = self.logClusters[index]
        clusterType = make_list(cluster.get("type") or cluster.get('types'))
        if clusterType:
          clusterType = clusterType[0]
        return clusterType
      def add_cluster_type_to_instruction(self,index,instruction):
        clusterType = self.get_cluster_type_from_index(index)
        instruction['type']=clusterType
        return instruction
      
      def add_cluster_types_to_instructions(self,instructions,indexStart=0):
        new_instructions = []
        for i,instruction in enumerate(instructions):
          index = i+indexStart
          instruction = self.add_cluster_type_to_instruction(index,instruction)
          new_instructions.append(instruction)
        return new_instructions
