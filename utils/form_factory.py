

class FormFactory(Object):
    template = 
    '''<div class="control-group">
      <label class="control-label">{{fieldname}}<span style="color:red">*</span>: </label>
      <div class="controls">
       <input name="email" type="text" placeholder="example@example.com" value="{{o.email}}">
       </div>
    </div>'''