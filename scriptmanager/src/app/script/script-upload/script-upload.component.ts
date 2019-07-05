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

  public onFileSave() {
    console.log(this.scriptFile)
    this.uploadfileService.postFile(this.tid, this.lid, this.scriptFile)
      .subscribe(
        (res) => {
          this.router.navigateByUrl("/view/" + this.tid + "/" + this.lid + "/" + this.tutorialName);
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
    }

  }

  public saveHtmlData() {
    // console.log(this.Htmldata);
    this.Htmldata = this.editorForm.get('data').value;
    this.createScriptService.postScript(
      this.tid, this.lid,
      {
        "details": this.Htmldata,
        "type": 'template'
      }
    ).subscribe(
      (res) => {
        this.router.navigateByUrl("/view/" + this.tid + "/" + this.lid + "/" + this.tutorialName);
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
    this.tutorialName = this.route.snapshot.params['tutorialName']
    this.editorForm = new FormGroup({
      'data': new FormControl()
    })

  }

}
