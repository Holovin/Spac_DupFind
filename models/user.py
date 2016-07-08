class User:
    id = 0
    name = " "

    hist = []
    sess = []

    def __init__(self, id, name, hist=[], sess=[]):
        self.id = id
        self.name = name
        self.hist = hist
        self.sess = sess
        return

    def get_var_dict(self, var_name):
        if not hasattr(self, var_name):
            return None

        out = []

        for item in getattr(self, var_name):
            out.append(item.__dict__)

        return out

    def add_var(self, var_name, data):
        if not hasattr(self, var_name):
            return None

        getattr(self, var_name).append(data)
        return

    def merge_var(self, var_name, old_user):
        new_items = []

        if not hasattr(old_user, var_name) or not hasattr(self, var_name):
            return False

        for o in getattr(self, var_name):
            if o not in getattr(old_user, var_name):
                new_items.append(o.__dict__)

        getattr(self, var_name).extend(new_items)

        return new_items
