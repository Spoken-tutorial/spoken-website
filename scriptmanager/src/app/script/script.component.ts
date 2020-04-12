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
  @Output() insertSlideEmitter = new EventEmitter<number>();
  @Output() duplicateSlideEmitter = new EventEmitter<number>();
  @Input() nav: any;
  @Input() displaySave: boolean = false;
  @Input() autosave: boolean = false;
  public tid;
  public lid;
  public vid;
  public tutorialName: any;

  constructor(public router: Router, public route: ActivatedRoute, public createscriptService: CreateScriptService) { }

  public getRelativeOrdering() {
    var relative_ordering = [];

    for (var i = 0; i < this.slides.length; i++) {
      const slide = this.slides[i];
      relative_ordering.push(slide.id);
    }

    return relative_ordering;
  }

  public onMoveSlide(data) {
    const index = data['index'];
    const move = data['move'];

    const newSlideIndex = index + move;

    if (!(newSlideIndex >= 0 && newSlideIndex < this.slides.length)) return;

    const temp = this.slides[index];
    this.slides[index] = this.slides[newSlideIndex];
    this.slides[newSlideIndex] = temp;

    if (this.nav == "create") return;
    
    const scriptId = this.slides[0]['script'];
    // const relativeOrdering = this.getRelativeOrdering().join(',');
    const slideid = this.slides[newSlideIndex].id
    this.createscriptService.modifyOrdering(scriptId, move, slideid)
      .subscribe(
        (res) => {
          new Noty({
            type: 'success',
            layout: 'topRight',
            theme: 'metroui',
            closeWith: ['click'],
            text: 'The script is sucessfully updated!',
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
  
  public getEmptySlide() {
    return {
      id: '-1',
      cue: '',
      narration: '',
      order: '',
      script: ''
    }
  }

  public addSlide() {
    this.slides.push(this.getEmptySlide());
    const index = this.slides.length - 1;
    this.insertSlideEmitter.emit(index);
  }
  
  //remove slides after clicking on cross icon
  public onRemoveSlide(index) {
    if (this.slides[index]['id'] != '') {
      this.createscriptService.deleteScript(
        this.tid, this.lid, this.vid, this.slides[index]['id']
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
    this.insertSlideEmitter.emit(index);
  }

  public onDuplicateSlide(index) {
    this.slides.splice(index, 0, this.getEmptySlide());
    this.slides[index].cue = this.slides[index - 1].cue;
    this.slides[index].narration = this.slides[index - 1].narration;
    this.duplicateSlideEmitter.emit(index);
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
    // this.addSlide();
    this.route.params.subscribe(params => {
      this.tid = +params['tid'];
    });
    this.lid = this.route.snapshot.params['lid']
    this.tutorialName = this.route.snapshot.params['tutorialName']
    this.vid = this.route.snapshot.params['vid']
  }

}
