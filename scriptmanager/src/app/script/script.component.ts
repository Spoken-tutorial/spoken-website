import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-script',
  templateUrl: './script.component.html',
  styleUrls: ['./script.component.sass']
})
export class ScriptComponent implements OnInit {
  @Input() slides: any;
  @Output() onSaveScript = new EventEmitter<any>();

  constructor() { }

  public addSlide() {
    this.slides.push(
      {
        cue: '', 
        narration: ''
      }
    );
  }

  public onRemoveSlide(index) {
    this.slides.splice(index, 1);
  }

  public saveScript() {
    this.onSaveScript.emit(this.slides);
  }

  ngOnInit() {
    this.addSlide();
  }

}
