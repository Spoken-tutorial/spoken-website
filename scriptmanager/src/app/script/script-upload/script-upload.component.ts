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
  private id: number;
  public tutorialName: any;
  public scriptFile: any;
  public scriptFileName: any;
  public uploadButton: boolean = false;
  public Htmldata: any;
  editorForm: FormGroup;
  public Editor = ClassicEditor;
  public ckeditorConfig = {
    toolbar: ['heading', '|', 'bold', 'italic', 'bulletedList', 'numberedList', '|', 'undo', 'redo']
  }

  constructor(
    public router: Router,
    private route: ActivatedRoute,
    public uploadfileService: UploadFileService,
    public createScriptService: CreateScriptService
  ) { }

  public onFileSave(file: any) {
    console.log(file)
    this.uploadfileService.postFile(this.id, file)
      .subscribe(
        (res) => {
          this.router.navigateByUrl("/view/" + this.id + "/" + this.tutorialName);
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
      // console.log("file upsupported")
    }

  }

  public saveHtmlData() {
    // console.log(this.Htmldata);
    this.Htmldata = this.editorForm.get('data').value;
    this.createScriptService.postScript(
      this.id,
      {
        "details": this.Htmldata,
        "type" : 'template'
      }
    ).subscribe(
      (res) => {
        this.router.navigateByUrl("/view/" + this.id + "/" + this.tutorialName);
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
      this.id = +params['id'];
    });
    this.tutorialName = this.route.snapshot.params['tutorialName']

    this.editorForm = new FormGroup({
      'data': new FormControl()
    })

  }

}
