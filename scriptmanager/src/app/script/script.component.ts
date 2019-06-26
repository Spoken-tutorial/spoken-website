import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Router } from "@angular/router";
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from 'src/app/_service/create-script.service';

@Component({
  selector: 'app-script',
  templateUrl: './script.component.html',
  styleUrls: ['./script.component.sass']
})

export class ScriptComponent implements OnInit {
  @Input() slides: any;
  @Output() onSaveScript = new EventEmitter<any>();
  @Output() File = new EventEmitter<any>();
  @Input() nav: any;
  @Input() displaySave: boolean = false;
  public id;
  public tutorialName: any;
  public scriptFile : any;
  public scriptFileName:any;
  public uploadButton : boolean = false;
  constructor(public router: Router, public route: ActivatedRoute, public createscriptService: CreateScriptService) { }

  public addSlide() {
    this.slides.push(
      {
        id: '',
        cue: '',
        narration: '',
        order: '',
        script: ''
      }
    );
  }

  public onRemoveSlide(index) {
    if (this.slides[index]['id'] != '') {
      this.createscriptService.deleteScript(
        this.id, this.slides[index]['id']
      ).subscribe(
        (res) => {
          new Noty({
            type: 'success',
            layout: 'topRight',
            theme: 'metroui',
            closeWith: ['click'],
            text: 'The slide is sucessfully deleted!',
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

    };
    this.slides.splice(index, 1);
  }

  public saveScript() {
    this.onSaveScript.emit(this.slides);
  }

  public onSaveSlide(slide) {
    this.onSaveScript.emit(slide);
  }

  public onFileChange(file){
    this.scriptFile = file.target.files[0];
    this.scriptFileName = file.target.files[0].name;
    var fileExtension = this.scriptFileName.split('.').pop();
    if(fileExtension=='docx'){
      this.uploadButton = true;
      this.scriptFileName = file.target.files[0].name;
    }
    else{
      this.scriptFileName = "Only docx supported";
      this.uploadButton=false;
      console.log("file upsupported")
    }
    
  }

  public onFileSave(){
    this.File.emit(this.scriptFile);
  }

  ngOnInit() {
    this.addSlide();
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.tutorialName = this.route.snapshot.params['tutorialName']
  }

}
