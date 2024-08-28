from kabaret import flow
from kabaret.flow.object import _Manager
from libreflow.baseflow.file import TrackedFile
from libreflow.baseflow.shot import Shot, Sequence
from libreflow.baseflow.film import Film
from libreflow.baseflow.asset import Asset, AssetFamily, AssetType

class DeleteAction(flow.Action):
    _MANAGER_TYPE = _Manager

    ICON = ('icons.gui', 'delete')

    _entity = flow.Parent()
    _map = flow.Parent(2)

    entity_name = flow.SessionParam('').ui(label='')

    def allow_context(self, context):
        return context

    def get_buttons(self):

        if hasattr(self._entity, 'display_name') and self._entity.display_name.get() != '':
            self._name = self._entity.display_name.get()
        else : self._name = self._entity.name()

        self.message.set(f'<b><h2>You are about to delete {self._name} </h2> Please enter the item name to confirm:</b>')
        return['Delete', 'Cancel']

    def run(self, button):
        self.message.set(f'<b><h2>You are about to delete {self._name} </h2> Please enter the item name to confirm:</b>')

        if button == 'Cancel':
            return

        if self.entity_name.get() == self._name :
            map = self._map
            map.remove(self._entity.name())
            map.touch()

        else :
            msg = self.message.get()
            msg += ("<font color=red><br/>Wrong entity name</font>")
            self.message.set(msg)
            return self.get_result(close=False)


        # path_list = []

        # items = self._map.mapped_items()
        # print(items)

        # for item in items:
        #     if os.path.isdir(item.path.get()):
        #         shutil.rmtree(item.path.get())

        #     if isinstance(item, Film):
        #         seq_list = item.sequences.mapped_items()
        #         for seq in seq_list:
        #             seq.shots.clear()
        #         item.sequences.clear()
        #         path_list.append(item.name())
        #         self._map.remove(item.name())


        #     elif isinstance(item, Sequence):
        #         item.shots.clear()
        #         self._map.remove(item.name()) 

            
        #     elif isinstance(item, Shot):
        #         self._map.remove(item.name())

        #     self._map.touch()


def delete_anything(parent):
    if isinstance(parent, (Film, Sequence, Shot, TrackedFile, Asset, AssetFamily, AssetType)):
        r = flow.Child(DeleteAction)
        r.name = 'delete'
        r.index = None
        r.ui(dialog_size=(600,300))
        return r


def install_extensions(session):
    return {
        "delete_anything": [
            delete_anything,
        ]
    }


from . import _version
__version__ = _version.get_versions()['version']
