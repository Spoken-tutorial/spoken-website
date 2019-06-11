import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import {Router} from "@angular/router";
@Component({
  selector: 'app-script',
  templateUrl: './script.component.html',
  styleUrls: ['./script.component.sass']
})
export class ScriptComponent implements OnInit {
  @Input() slides: any;
  @Output() onSaveScript = new EventEmitter<any>();

  constructor(public router:Router) { }

  public addSlide() {
    this.slides.push(
      {
        cue: '',
        narration: '',
      }
    );
  }

  public onRemoveSlide(index) {
    this.slides.splice(index, 1);
  }

  public saveScript() {
    this.onSaveScript.emit(this.slides);
    this.router.navigateByUrl("/")
    
  }

  ngOnInit() {
    this.addSlide();
  }

}
