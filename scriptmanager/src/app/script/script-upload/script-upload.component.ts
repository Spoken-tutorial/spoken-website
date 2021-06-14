import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UploadFileService } from '../../_service/upload-file.service'
import { CreateScriptService } from '../../_service/create-script.service'
import * as ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import { FormGroup, FormControl } from '@angular/forms';

@Component({
  selector: 'app-script-upload',
  templateUrl: './script-upload.component.html',
  styleUrls: ['./script-upload.component.sass']
})
export class ScriptUploadComponent implements OnInit {
  private tid: number;
  private lid: number;
  private vid: number;
  public tutorialName: any;
  public scriptFile: any;
  public scriptFileName: any;
  public uploadButton: boolean = false;
  public Htmldata = "";
  editorForm: FormGroup;
  public Editor = ClassicEditor;
  public ckeditorConfig = {
    toolbar: ['heading', '|', 'bold', 'italic', 'bulletedList', 'numberedList', '|', 'undo', 'redo']
  }

  public quillStyles = {
    'height': '200px',
    'border': '1px solid #ccc',
    'margin': 'auto',
    // 'max-width': '600px'
  }

  constructor(
    public router: Router,
    private route: ActivatedRoute,
    public uploadfileService: UploadFileService,
    public createScriptService: CreateScriptService
  ) { }
  // argument:called on click of submit button
  // what it does: make an api call(POST request) with the file variable containing the latest file selected by the user. 
  // returns: void
  public onFileSave() {
    this.uploadfileService.postFile(this.tid, this.lid, this.vid, this.scriptFile)
      .subscribe(
        (res) => {
          this.router.navigateByUrl("/view/" + this.tid + "/" + this.lid + "/" + this.tutorialName + "/" + this.vid);
          new Noty({
            type: 'success',
            layout: 'topRight',
            theme: 'metroui',
            closeWith: ['click'],
            text: 'The script is sucessfully created!',
            animation: {
              open: 'animated fadeInRight',
              close: 'animated fadeOutRight'
            },
            timeout: 4000,
            killer: true
          }).show();
        },
        (error) => {
          new Noty({
            type: 'error',
            layout: 'topRight',
            theme: 'metroui',
            closeWith: ['click'],
            text: 'Woops! There seems to be an error.',
            animation: {
              open: 'animated fadeInRight',
              close: 'animated fadeOutRight'
            },
            timeout: 4000,
            killer: true
          }).show();
        }
      )

  }
  // argument:file which is uploaded by the user
  // what it does: updates the file variable with the recent file selected by the user and validates for valid extensions 
  // returns: void
  public onFileChange(file) {
    this.scriptFile = file.target.files[0];
    this.scriptFileName = file.target.files[0].name;
    var fileExtension = this.scriptFileName.split('.').pop();
    if (fileExtension == 'docx' || fileExtension == 'odt' || fileExtension == 'doc') {
      this.uploadButton = true;
      this.scriptFileName = file.target.files[0].name;
    }
    else {
      this.scriptFileName = "Only docx/doc/odt supported";
      this.uploadButton = false;
    }

  }
  // argument:HTML data which is pasted by the user in the editor(user pastes the whole table in the editor)
  // what it does : makes an api call (POST request)  with the html data so that server saves the whole table 
  // returns: Gives a green notification on success otherwise a red notification
  public saveHtmlData() {
    this.Htmldata = this.editorForm.get('data').value;
    this.createScriptService.postScript(
      this.tid, this.lid, this.vid,
      {
        "details": this.Htmldata,
        "type": 'template'
      }
    ).subscribe(
      (res) => {
        this.router.navigateByUrl("/view/" + this.tid + "/" + this.lid + "/" + this.tutorialName + "/" + this.vid);
        new Noty({
          type: 'success',
          layout: 'topRight',
          theme: 'metroui',
          closeWith: ['click'],
          text: 'The script is sucessfully created!',
          animation: {
            open: 'animated fadeInRight',
            close: 'animated fadeOutRight'
          },
          timeout: 4000,
          killer: true
        }).show();
      },
      (error) => {
        new Noty({
          type: 'error',
          layout: 'topRight',
          theme: 'metroui',
          closeWith: ['click'],
          text: 'Woops! There seems to be an error.',
          animation: {
            open: 'animated fadeInRight',
            close: 'animated fadeOutRight'
          },
          timeout: 4000,
          killer: true
        }).show();
      }
    );
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.tid = +params['tid'];
    });
    this.lid = this.route.snapshot.params['lid']
    this.vid = this.route.snapshot.params['vid']
    this.tutorialName = this.route.snapshot.params['tutorialName']
    
    //editorform holds the html data
    this.editorForm = new FormGroup({
      'data': new FormControl()
    })

  }

}
