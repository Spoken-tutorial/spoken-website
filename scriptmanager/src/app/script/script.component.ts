import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Router } from "@angular/router";
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from 'src/app/_service/create-script.service';
// This component is called by create and edit components for major functioning
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
  public tid;
  public lid;
  public tutorialName: any;

  constructor(public router: Router, public route: ActivatedRoute, public createscriptService: CreateScriptService) { }

  //what it does: add more slides on clicking on plus icon

  public getEmptySlide() {
    return {
      id: '',
      cue: '',
      narration: '',
      order: '',
      script: ''
    }
  }
  public addSlide() {
    this.slides.push(this.getEmptySlide());
  }
  
  //remove slides after clicking on cross icon
  public onRemoveSlide(index) {
    if (this.slides[index]['id'] != '') {
      this.createscriptService.deleteScript(
        this.tid, this.lid, this.slides[index]['id']
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

  public onInsertSlide(index) {
    this.slides.splice(index, 0, this.getEmptySlide());
  }
  //calls the component which called script component and gives the slides array which needs to be saved in the database.
  public saveScript() {
    this.onSaveScript.emit(this.slides);
  }

  //saves a particular slide
  public onSaveSlide(slide) {
    this.onSaveScript.emit(slide);
  }

  ngOnInit() {
    this.addSlide();
    this.route.params.subscribe(params => {
      this.tid = +params['tid'];
    });
    this.lid = this.route.snapshot.params['lid']
    this.tutorialName = this.route.snapshot.params['tutorialName']
  }

}
