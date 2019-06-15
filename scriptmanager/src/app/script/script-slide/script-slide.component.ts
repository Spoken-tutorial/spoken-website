import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-script-slide',
  templateUrl: './script-slide.component.html',
  styleUrls: ['./script-slide.component.sass']
})
export class ScriptSlideComponent implements OnInit {
  @Input() slide: any;
  @Input() index: number;
  @Output() removeSlideEmitter = new EventEmitter<number>();
  @Output() getCommentEmitter = new EventEmitter<any>();
  @Input() view: boolean=false;
  public comments: any = [];

  constructor() { }

  public removeSlide() {
    this.removeSlideEmitter.emit(this.index);
  }

  public viewComment(index) {
    // console.log(this.index);
    this.comments = [
      {
        "slideId": index,
        "user": "Reviewer 1", 
        "comment": "This comment is from reviewer 1"
      },
      {
        "slideId": index,
        "user": "Reviewer 2", 
        "comment": "This comment is from reviewer 2"
      },
      {
        "slideId": index,
        "user": "Reviewer 3", 
        "comment": "This comment is from reviewer 3"
      },
      {
        "slideId": index,
        "user": "Reviewer 4", 
        "comment": "This comment is from reviewer 4"
      }
    ];
    console.log(this.comments)
    this.getCommentEmitter.emit(this.comments);

  }

  cueKey(event) { this.slide.cue = event.target.value;}
  narrationKey(event) { this.slide.narration = event.target.value;}

  ngOnInit() {
  }

}
