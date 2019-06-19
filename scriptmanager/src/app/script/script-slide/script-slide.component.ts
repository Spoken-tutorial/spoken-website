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
  @Output() saveSlideEmitter = new EventEmitter<any>();
  @Input() view: boolean = false;
  public comment = false;


  constructor() { }

  public removeSlide() {
    this.removeSlideEmitter.emit(this.index);
  }

  public saveSlide() {
    this.saveSlideEmitter.emit(this.slide);
  }

  cueKey(event) { this.slide.cue = event.target.value; }
  narrationKey(event) { this.slide.narration = event.target.value; }

  ngOnInit() {
  }

}
